"""Processo worker: é aqui (e só aqui) que o código do aluno é executado.

O worker importa o Qiskit ao nascer (pré-aquecimento) e depois atende um job
por vez. Se travar ou estourar a memória, o pool o mata e cria outro.
"""

from __future__ import annotations

import sys

MEMORY_LIMIT_BYTES = 4 * 1024**3


def _limit_memory() -> None:
    # RLIMIT_AS só é confiável no Linux. No Windows/macOS a proteção é o teto
    # de qubits + timeout; um Job Object no Windows fica para a fase de empacotamento.
    if sys.platform != "linux":
        return
    import resource

    _, hard = resource.getrlimit(resource.RLIMIT_AS)
    limit = MEMORY_LIMIT_BYTES if hard == resource.RLIM_INFINITY else min(MEMORY_LIMIT_BYTES, hard)
    resource.setrlimit(resource.RLIMIT_AS, (limit, hard))


def handle(job: dict, emit=None) -> dict:
    """Atende um job. Erros do aluno voltam como {ok: False, error: {...}}.

    `emit` envia eventos ao servidor enquanto o job roda (progresso de treino).
    """
    from . import geometry, i18n, simulator, tracer, validation

    i18n.set_lang(job.get("lang"))
    kind = job.get("type")
    try:
        if kind == "run":
            reporter = tracer.Reporter(emit if job.get("stream") else None)
            trajectory, execution = _simulate(job, reporter)
            result = {"ok": True, "stdout": execution.stdout, **geometry.describe_trajectory(trajectory)}
            if execution.reports:
                result["training"] = {"series": execution.reports}
            if job.get("analysis"):
                result["analysis"] = run_analysis(job["analysis"], execution.namespace)
            return result
        if kind == "shots":
            trajectory, execution = _simulate(job)
            if execution.circuit is not None:
                return {"ok": True, **simulator.sample_counts(
                    execution.circuit,
                    shots=int(job.get("shots", 1024)),
                    seed=int(job.get("seed", 0)),
                    max_qubits=_max_qubits(job),
                )}
            return {"ok": True, **_sample_final_state(trajectory, int(job.get("shots", 1024)), int(job.get("seed", 0)))}
        if kind == "export":
            return {"ok": True, **export_circuit(job)}
        if kind == "validate":
            return {"ok": True, **validation.validate(job["code"], job["lesson"])}
        if kind == "ping":
            return {"ok": True}
        return _error(i18n.t("run.unknown_job", kind=kind), kind="internal")
    except tracer.UserCodeError as exc:
        return _error(exc.message, exc.line, exc.kind)
    except simulator.SimulationError as exc:
        return _error(exc.message, exc.line, "simulation")
    except MemoryError:
        return _error(i18n.t("run.memory"), kind="memory")
    except Exception as exc:  # noqa: BLE001 - o worker nunca deve morrer por um job
        return _error(i18n.t("run.internal", detail=f"{type(exc).__name__}: {exc}"), kind="internal")


def _max_qubits(job: dict) -> int:
    from .simulator import DEFAULT_MAX_QUBITS

    return int(job.get("max_qubits") or DEFAULT_MAX_QUBITS)


def _simulate(job: dict, reporter=None):
    """Executa o código e devolve (trajetória, execução), para Qiskit ou PennyLane.

    Lições PennyLane rodam sem rastreamento linha a linha (treinos ficam rápidos);
    no laboratório livre, um QNode é usado quando não há QuantumCircuit.
    """
    from . import pl, simulator, tracer

    pennylane = job.get("framework") == "pennylane"
    execution = tracer.execute(
        job["code"], job.get("hidden_setup"), job.get("inputs"),
        trace=not pennylane, require_circuit=False, reporter=reporter,
    )
    if execution.circuit is not None and not pennylane:
        trajectory = simulator.run_trajectory(
            execution.circuit, execution.lines, seed=int(job.get("seed", 0)), max_qubits=_max_qubits(job)
        )
        return trajectory, execution
    spec = job.get("qnode") or {}
    try:
        qnode = pl.find_qnode(execution.namespace, spec.get("name"))
    except tracer.UserCodeError:
        if pennylane:
            raise
        raise tracer.UserCodeError(_no_circuit_message(), kind="no_circuit") from None
    ops, lines, n = pl.trace_qnode(qnode, pl.qnode_arguments(qnode, execution.namespace, spec.get("args")))
    trajectory = simulator.run_ops_trajectory(ops, lines, n, seed=int(job.get("seed", 0)), max_qubits=_max_qubits(job))
    return trajectory, execution


EXPORT_FORMATS = {"qasm2": "OpenQASM 2.0", "qasm3": "OpenQASM 3.0"}


def export_circuit(job: dict) -> dict:
    """O circuito do código em OpenQASM 2 ou 3 (Qiskit ou o QNode PennyLane)."""
    from qiskit import qasm2, qasm3

    from . import i18n, pl, tracer

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
            raise tracer.UserCodeError(i18n.t("export.noise"), kind="export")
        try:
            source = qml.to_openqasm(qnode)(*args)
            if fmt == "qasm2":
                return {"format": fmt, "text": source}
            circuit = qasm2.loads(source, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
        except Exception as exc:  # noqa: BLE001 - porta sem equivalente em OpenQASM
            raise tracer.UserCodeError(i18n.t("export.unsupported", format=label, detail=_short(exc)), kind="export") from None
    try:
        text = qasm2.dumps(circuit) if fmt == "qasm2" else qasm3.dumps(circuit)
    except Exception as exc:  # noqa: BLE001
        raise tracer.UserCodeError(i18n.t("export.unsupported", format=label, detail=_short(exc)), kind="export") from None
    return {"format": fmt, "text": text}


def _short(exc: BaseException) -> str:
    text = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
    return text[:200]


def _no_circuit_message() -> str:
    from .i18n import t

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
    """Roda o analysis.py da lição (conteúdo confiável) sobre o namespace do aluno.

    O resultado alimenta as visualizações de treino (paisagem de custo, curva de
    convergência, grafo, fronteira de decisão). Erros viram {"error": ...} e não
    impedem o resto da visualização.
    """
    try:
        module: dict = {"__name__": "qlp_analysis"}
        exec(compile(code, "<analysis>", "exec"), module)
        return to_json(module["analyze"](namespace))
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


def to_json(value):
    """Converte arrays e números do NumPy/PennyLane em tipos JSON."""
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


def _error(message: str, line: int | None = None, kind: str = "runtime") -> dict:
    return {"ok": False, "error": {"message": message, "line": line, "kind": kind}}


def worker_main(connection) -> None:
    """Ponto de entrada do processo filho."""
    _limit_memory()
    from . import geometry, simulator, tracer, validation  # noqa: F401 - pré-aquecimento

    try:  # o PennyLane leva ~1 s para importar: melhor agora do que na primeira lição
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
