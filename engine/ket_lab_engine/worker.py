"""Worker process: this is where (and only where) the student's code is executed.

The worker imports Qiskit on startup (warm-up) and then serves one job
at a time. If it hangs or runs out of memory, the pool kills it and creates another.
"""

from __future__ import annotations

import sys

MEMORY_LIMIT_BYTES = 4 * 1024**3


def _limit_memory() -> None:
    # RLIMIT_AS is only reliable on Linux. On Windows/macOS the protection is the qubit
    # cap + timeout; a Job Object on Windows is left for the packaging phase.
    if sys.platform != "linux":
        return
    import resource

    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    limit = MEMORY_LIMIT_BYTES if hard == resource.RLIM_INFINITY else min(MEMORY_LIMIT_BYTES, hard)
    resource.setrlimit(resource.RLIMIT_AS, (limit, hard))


def handle(job: dict, emit=None) -> dict:
    """Serves one job. Student errors come back as {ok: False, error: {...}}.

    `emit` sends events to the server while the job runs (training progress).
    """
    from . import geometry, messages, simulator, tracer, validation

    kind = job.get("type")
    try:
        if kind == "run" and job.get("framework") == "python":
            return {"ok": True, **_run_python(job)}
        if kind == "run":
            reporter = tracer.Reporter(emit if job.get("stream") else None)
            collector = geometry.SnapshotCollector()
            trajectory, execution = _simulate(job, reporter, collector)
            result = {"ok": True, "stdout": execution.stdout, **geometry.describe_trajectory(trajectory, collector)}
            if execution.reports:
                result["training"] = {"series": execution.reports}
            if job.get("analysis"):
                result["analysis"] = run_analysis(job["analysis"], execution.full_namespace())
            return result
        if kind == "shots":
            execution = _execute(job)
            if emit is not None:
                emit({"event": "phase", "name": "sampling"})  # a timeout from here on is a heavy run, not a stuck loop
            if execution.circuit is not None and job.get("framework") != "pennylane":
                # Straight to sampling: the step-by-step trajectory is not needed for counts.
                return {"ok": True, **simulator.sample_counts(
                    execution.circuit,
                    shots=int(job.get("shots", 1024)),
                    seed=int(job.get("seed", 0)),
                    max_qubits=_max_qubits(job),
                )}
            trajectory = _trajectory(job, execution, simulator.FinalOnly())
            return {"ok": True, **_sample_final_state(trajectory, int(job.get("shots", 1024)), int(job.get("seed", 0)))}
        if kind == "export":
            return {"ok": True, **export_circuit(job)}
        if kind == "validate":
            return {"ok": True, **validation.validate(job["code"], job["lesson"])}
        if kind == "ping":
            return {"ok": True}
        return _error(messages.t("run.unknown_job", kind=kind), kind="internal")
    except tracer.UserCodeError as exc:
        return _error(exc.message, exc.line, exc.kind, exc.stdout)
    except simulator.SimulationError as exc:
        return _error(exc.message, exc.line, "simulation", getattr(exc, "stdout", ""))
    except MemoryError:
        return _error(messages.t("run.memory"), kind="memory")
    except KeyboardInterrupt:
        raise
    except SystemExit:  # raised outside the traced execution (e.g. inside a lesson check): same report
        return _error(messages.t("run.exit"), kind="runtime")
    except Exception as exc:  # noqa: BLE001 - the worker must never die because of a job
        return _error(messages.t("run.internal", detail=f"{type(exc).__name__}: {exc}"), kind="internal")


def _run_python(job: dict) -> dict:
    """Lesson without a circuit (math kit): runs and shows the student's variables."""
    from . import tracer

    execution = tracer.execute(
        job["code"], job.get("hidden_setup"), job.get("inputs"), trace=False, require_circuit=False
    )
    reply = {
        "stdout": execution.stdout,
        "num_qubits": 0,
        "num_clbits": 0,
        "steps": [],
        "snapshots": [],
        "clbits": [],
        "has_measurement": False,
        "variables": describe_variables(execution.namespace),
    }
    if job.get("analysis"):  # same field and shape as the circuit branch; a failing analysis is {"error": ...}
        reply["analysis"] = run_analysis(job["analysis"], execution.full_namespace())
    return reply


HIDDEN_NAMES = {"run_shots", "report"}
MAX_VARIABLES = 40


def describe_variables(namespace: dict) -> list[dict]:
    """The student's numeric variables, in the order they were created, ready to display."""
    import numpy as np

    rows = []
    for name, value in namespace.items():
        if name.startswith("_") or name in HIDDEN_NAMES or callable(value) or type(value).__name__ == "module":
            continue
        text = _format_value(value, np)
        if text is not None:
            rows.append({"name": name, "type": _type_name(value, np), "value": text})
        if len(rows) >= MAX_VARIABLES:
            break
    return rows


def _type_name(value, np) -> str:
    if isinstance(value, np.ndarray):
        return f"array {'×'.join(map(str, value.shape))}"
    return type(value).__name__


def _format_value(value, np) -> str | None:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float, complex, np.number)):
        return np.array2string(np.asarray(value), precision=4, suppress_small=True)
    if isinstance(value, (list, tuple)) and len(value) <= 32 and all(isinstance(v, (int, float, complex, np.number)) for v in value):
        value = np.asarray(value)
    if isinstance(value, np.ndarray) and value.ndim <= 2 and value.size <= 64 and np.issubdtype(value.dtype, np.number):
        return np.array2string(value, precision=4, suppress_small=True, max_line_width=60)
    if isinstance(value, str) and len(value) <= 80:
        return repr(value)
    return None


def _max_qubits(job: dict) -> int:
    from .simulator import DEFAULT_MAX_QUBITS

    return int(job.get("max_qubits") or DEFAULT_MAX_QUBITS)


def _execute(job: dict, reporter=None):
    """Runs the learner's code (Qiskit with line tracing; PennyLane without it)."""
    from . import tracer

    pennylane = job.get("framework") == "pennylane"
    return tracer.execute(
        job["code"], job.get("hidden_setup"), job.get("inputs"),
        trace=not pennylane, require_circuit=False, reporter=reporter,
    )


def _trajectory(job: dict, execution, observer=None):
    """Step-by-step simulation of what the code built, for Qiskit or PennyLane.

    In the free lab, a QNode is used when there is no QuantumCircuit. With an `observer` the states are
    handed over one by one instead of being kept (see simulator.run_trajectory).
    """
    from . import pl, simulator, tracer

    pennylane = job.get("framework") == "pennylane"
    if execution.circuit is not None and not pennylane:
        try:
            return simulator.run_trajectory(
                execution.circuit, execution.lines, seed=int(job.get("seed", 0)), max_qubits=_max_qubits(job),
                observer=observer,
            )
        except simulator.SimulationError as exc:
            exc.stdout = execution.stdout  # print debugging still works when the circuit is refused
            raise
    spec = job.get("qnode") or {}
    try:
        qnode = pl.find_qnode(execution.namespace, spec.get("name"))
    except tracer.UserCodeError:
        if pennylane:
            raise
        raise tracer.UserCodeError(_no_circuit_message(), kind="no_circuit") from None
    ops, lines, n = pl.trace_qnode(qnode, pl.qnode_arguments(qnode, execution.namespace, spec.get("args")))
    return simulator.run_ops_trajectory(
        ops, lines, n, seed=int(job.get("seed", 0)), max_qubits=_max_qubits(job), observer=observer
    )


def _simulate(job: dict, reporter=None, observer=None):
    """Runs the code and returns (trajectory, execution), for Qiskit or PennyLane.

    PennyLane lessons run without line-by-line tracing (training stays fast).
    """
    execution = _execute(job, reporter)
    return _trajectory(job, execution, observer), execution


EXPORT_FORMATS = {"qasm2": "OpenQASM 2.0", "qasm3": "OpenQASM 3.0"}


def export_circuit(job: dict) -> dict:
    """The code's circuit in OpenQASM 2 or 3 (Qiskit or the PennyLane QNode)."""
    from qiskit import qasm2, qasm3

    from . import messages, pl, tracer

    fmt = job.get("format") if job.get("format") in EXPORT_FORMATS else "qasm3"
    label = EXPORT_FORMATS[fmt]
    pennylane = job.get("framework") == "pennylane"
    execution = tracer.execute(
        job["code"], job.get("hidden_setup"), job.get("inputs"), trace=not pennylane, require_circuit=False
    )
    circuit = execution.circuit if not pennylane else None
    if circuit is None:
        import pennylane as qml

        spec = job.get("qnode") or {}
        try:
            qnode = pl.find_qnode(execution.namespace, spec.get("name"))
        except tracer.UserCodeError:
            if pennylane:
                raise
            raise tracer.UserCodeError(_no_circuit_message(), kind="no_circuit") from None
        args = pl.qnode_arguments(qnode, execution.namespace, spec.get("args"))
        ops, _, _ = pl.trace_qnode(qnode, args)
        if any(op.kind == "channel" for op in ops):
            raise tracer.UserCodeError(messages.t("export.noise"), kind="export")
        try:
            source = qml.to_openqasm(qnode)(*args)
            if fmt == "qasm2":
                return {"format": fmt, "text": source}
            circuit = qasm2.loads(source, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
        except Exception as exc:  # noqa: BLE001 - gate with no OpenQASM equivalent
            raise tracer.UserCodeError(messages.t("export.unsupported", format=label, detail=_short(exc)), kind="export") from None
    try:
        text = qasm2.dumps(circuit) if fmt == "qasm2" else qasm3.dumps(circuit)
    except Exception as exc:  # noqa: BLE001
        raise tracer.UserCodeError(messages.t("export.unsupported", format=label, detail=_short(exc)), kind="export") from None
    return {"format": fmt, "text": text}


def _short(exc: BaseException) -> str:
    text = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
    return text[:200]


def _no_circuit_message() -> str:
    from .messages import t

    return t("run.no_circuit")


def _sample_final_state(trajectory, shots: int, seed: int) -> dict:
    import numpy as np

    from .simulator import MAX_SHOTS, state_probabilities

    shots = max(1, min(shots, MAX_SHOTS))
    probabilities = state_probabilities(trajectory.states[-1])
    probabilities = probabilities / probabilities.sum()
    samples = np.random.default_rng(seed).choice(len(probabilities), size=shots, p=probabilities)
    width = trajectory.num_qubits
    counts: dict[str, int] = {}
    for sample in samples:
        key = format(int(sample), f"0{width}b")
        counts[key] = counts.get(key, 0) + 1
    return {"shots": shots, "counts": dict(sorted(counts.items())), "measured": "qubits", "width": width}


def run_analysis(code: str, namespace: dict) -> dict:
    """Runs the lesson's analysis.py (trusted content) over the student's namespace.

    The result feeds the training visualizations (cost landscape, convergence
    curve, graph, decision boundary). Errors become {"error": ...} and do not
    block the rest of the visualization.
    """
    try:
        module: dict = {"__name__": "ket_lab_analysis"}
        exec(compile(code, "<analysis>", "exec"), module)
        return to_json(module["analyze"](namespace))
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


def to_json(value):
    """Converts NumPy/PennyLane arrays and numbers into JSON types."""
    import numpy as np

    if isinstance(value, dict):
        return {str(k): to_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json(v) for v in value]
    if hasattr(value, "tolist"):
        return to_json(np.asarray(value).tolist())
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if np.isfinite(number) else None
    if isinstance(value, (np.integer,)):
        return int(value)
    return value


def _error(message: str, line: int | None = None, kind: str = "runtime", stdout: str = "") -> dict:
    response = {"ok": False, "error": {"message": message, "line": line, "kind": kind}}
    if stdout:  # what the code printed before it failed, under the same field a successful run uses
        response["stdout"] = stdout
    return response


def worker_main(connection) -> None:
    """Entry point of the child process."""
    _limit_memory()
    from . import geometry, simulator, tracer, validation  # noqa: F401 - warm-up

    try:  # PennyLane takes ~1 s to import: better now than on the first lesson
        import pennylane  # noqa: F401
    except ImportError:
        pass

    connection.send({"event": "ready"})
    while True:
        try:
            job = connection.recv()
        except (EOFError, OSError):
            return
        if job is None:
            return
        connection.send(handle(job, connection.send))
