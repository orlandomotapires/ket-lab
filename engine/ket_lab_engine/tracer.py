"""Runs the student's code exactly once and records, for each instruction
added to a QuantumCircuit, the module-level line that originated it.

"State after line k" is not well defined when there are loops or functions, so
the unit of a step is the *instruction*. An instruction emitted inside a function
is attributed to the module-level line that called that function; inside a
`for`, to the line of the loop body.
"""

from __future__ import annotations

import ast
import contextlib
import io
import sys
import time
import traceback
from dataclasses import dataclass, field

from qiskit import QuantumCircuit

from . import guard
from .messages import t

USER_FILENAME = "<student>"
MAX_STDOUT_CHARS = 10_000


class UserCodeError(Exception):
    """Error attributable to the student's code, with the line when known."""

    def __init__(self, message: str, line: int | None = None, kind: str = "runtime", stdout: str = ""):
        super().__init__(message)
        self.message = message
        self.line = line
        self.kind = kind
        self.stdout = stdout  # what the code printed before it failed


@dataclass
class Execution:
    circuit: QuantumCircuit | None  # None in PennyLane code
    lines: list[int]  # source line of each instruction in circuit.data
    stdout: str = ""
    namespace: dict = field(default_factory=dict)
    reports: dict[str, list[float]] = field(default_factory=dict)
    # What the hidden setup defined under private names (the secret case, helpers): not in `namespace`,
    # which is what the learner's code ran in, but available to the lesson's own check.py and analysis.py.
    setup_private: dict = field(default_factory=dict)

    def full_namespace(self) -> dict:
        """The learner's namespace plus the setup's private names (for trusted lesson code only)."""
        return {**self.setup_private, **self.namespace}


MAX_REPORTS = 5_000
REPORT_INTERVAL_S = 0.1


class Reporter:
    """`report(...)` in the student's code: records metrics from a training loop.

    `report(cost)` records the "cost" series; `report(cost=c, accuracy=a)` records several.
    With `emit`, new values go out in batches while the code is still running
    (at most every REPORT_INTERVAL_S), so the curve appears epoch by epoch.
    """

    def __init__(self, emit=None):
        self.series: dict[str, list[float]] = {}
        self.emit = emit
        self._pending: dict[str, list[float]] = {}
        self._last_emit = 0.0
        self._count = 0

    def __call__(self, *args, **values):
        if len(args) > 1 or (args and "cost" in values):
            raise TypeError("report(value) or report(name=value, ...)")
        if args:
            values = {"cost": args[0], **values}
        if not values:
            raise TypeError("report(value) or report(name=value, ...)")
        if self._count >= MAX_REPORTS:
            return
        self._count += 1
        for name, value in values.items():
            number = _to_float(value)
            if number is None:
                raise TypeError(f"report(): {name} must be a number")
            self.series.setdefault(str(name), []).append(number)
            self._pending.setdefault(str(name), []).append(number)
        if self.emit is not None and time.monotonic() - self._last_emit >= REPORT_INTERVAL_S:
            self.flush()

    def flush(self) -> None:
        if self.emit is None or not self._pending:
            return
        self.emit({"event": "progress", "series": self._pending})
        self._pending = {}
        self._last_emit = time.monotonic()


def _to_float(value) -> float | None:
    """Real number from a float, int, NumPy scalar or one-element PennyLane tensor."""
    import numpy as np

    try:
        array = np.real(np.asarray(value, dtype=complex)).reshape(-1)
    except (TypeError, ValueError):
        return None
    if array.size != 1 or not np.isfinite(array[0]):
        return None
    return float(array[0])


class _CircuitWatcher:
    """Watches the namespace's QuantumCircuits and assigns lines to new instructions.

    The circuits already known are checked on every line event (one length comparison each). Looking for
    NEW circuits is what used to scan the whole namespace on every line; now it happens only when the
    namespace grew, or when the line that just ran binds a name (assignment, `for` target, `with ... as`,
    walrus), or when the code declares `global` somewhere (a function may then rebind a name).
    """

    def __init__(self, namespace: dict, tree: ast.AST | None = None):
        self.namespace = namespace
        self.current_line: int | None = None
        # id -> (circuit, lines, creation order). Keeping the circuit avoids id reuse.
        self.seen: dict[int, tuple[QuantumCircuit, list[int], int]] = {}
        self._tracked: list[tuple[QuantumCircuit, list[int]]] = []
        self._size = -1  # forces a full scan on the first line (circuits made by the hidden setup)
        bound, always = _bound_names(tree) if tree is not None else ({}, set())
        # Names to look at after each line: what it binds, plus the names some function may rebind with `global`.
        self._default = tuple(sorted(always))
        self._bound = {line: tuple(sorted(names | always)) for line, names in bound.items()}
        self._everything = tree is None  # without a tree there is no way to know: scan as before

    def flush(self) -> None:
        """Looks for new circuits (where one can have appeared) and attributes the new instructions."""
        namespace = self.namespace
        if self._everything or len(namespace) != self._size:
            self._size = len(namespace)
            for value in list(namespace.values()):
                if isinstance(value, QuantumCircuit) and id(value) not in self.seen:
                    self._register(value)
        else:
            for name in self._bound.get(self.current_line, self._default):
                value = namespace.get(name)
                if isinstance(value, QuantumCircuit) and id(value) not in self.seen:
                    self._register(value)
        self._attribute()

    def _attribute(self) -> None:
        """Gives the instructions added since the last look to the line that was running."""
        line = self.current_line or 0
        for circuit, lines in self._tracked:
            count = len(circuit)
            if count != len(lines):
                if count > len(lines):
                    lines.extend([line] * (count - len(lines)))
                else:
                    del lines[count:]

    def _register(self, circuit: QuantumCircuit) -> None:
        lines: list[int] = []
        self.seen[id(circuit)] = (circuit, lines, len(self.seen))
        self._tracked.append((circuit, lines))

    def trace(self, frame, event, arg):
        code = frame.f_code
        if code.co_filename != USER_FILENAME or code.co_name != "<module>":
            return None
        return self._trace_module

    def _trace_module(self, frame, event, arg):
        if event == "line":
            # The hot path (every line of every loop), written out instead of calling flush().
            namespace = self.namespace
            if self._everything or len(namespace) != self._size:
                self.flush()
            else:
                seen = self.seen
                for name in self._bound.get(self.current_line, self._default):
                    value = namespace.get(name)
                    if isinstance(value, QuantumCircuit) and id(value) not in seen:
                        self._register(value)
                for circuit, lines in self._tracked:
                    if len(circuit) != len(lines):
                        self._attribute()
                        break
            self.current_line = frame.f_lineno
        return self._trace_module


def _bound_names(tree: ast.AST) -> tuple[dict[int, set[str]], set[str]]:
    """Names each module-level line can bind (by line number), and the names declared `global`."""
    by_line: dict[int, set[str]] = {}
    always: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            always.update(node.names)
        if not isinstance(node, ast.stmt):
            continue
        if isinstance(getattr(node, "body", None), list):  # compound: only its header line(s)
            parts = [
                child for child in ast.iter_child_nodes(node)
                if not isinstance(child, (ast.stmt, ast.excepthandler, ast.match_case))
            ]
            last = node.body[0].lineno - 1 if node.body else node.lineno
        else:
            parts = [node]
            last = node.end_lineno or node.lineno
        names = {n.id for part in parts for n in ast.walk(part) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
        for line in range(node.lineno, max(last, node.lineno) + 1) if names else ():
            by_line.setdefault(line, set()).update(names)
    return by_line, always


def execute(
    code: str,
    hidden_setup: str | None = None,
    inputs: dict | None = None,
    *,
    trace: bool = True,
    require_circuit: bool = True,
    reporter: Reporter | None = None,
) -> Execution:
    """Runs the code and returns the main circuit with the line of each instruction.

    `inputs` are variables placed in the namespace before the hidden setup: this is how
    the validator varies, for example, the state that Alice teleports.
    """
    try:
        tree = guard.check(code)
    except SyntaxError as exc:
        raise UserCodeError(t("run.syntax", detail=exc.msg), exc.lineno, kind="syntax") from None
    except guard.CodeRejected as exc:
        issue = exc.issues[0]
        raise UserCodeError(issue.message, issue.line, kind="guard") from None

    namespace: dict = {"__name__": "__main__", "__builtins__": guard.restricted_builtins()}
    namespace["run_shots"] = _run_shots
    reporter = reporter or Reporter()
    namespace["report"] = reporter
    setup_private: dict = {}
    if hidden_setup:
        # The setup (lesson content, trusted) runs in a namespace of its own, with the case in `_KET_LAB_INPUT`.
        # The learner's code receives only its public names; the private ones (the secret, helpers) stay
        # behind, reachable only through the globals of the functions the setup defined.
        setup = dict(namespace)
        if inputs:
            setup.update(inputs)
        exec(compile(hidden_setup, "<setup>", "exec"), setup)
        namespace.update({name: value for name, value in setup.items() if not name.startswith("_")})
        setup_private = {name: value for name, value in setup.items() if name.startswith("_") and name not in namespace}

    watcher = _CircuitWatcher(namespace, tree)
    stdout = io.StringIO()
    compiled = compile(tree, USER_FILENAME, "exec")

    def printed() -> str:
        return stdout.getvalue()[:MAX_STDOUT_CHARS]

    previous_trace = sys.gettrace()
    try:
        with contextlib.redirect_stdout(stdout):
            # No tracing (PennyLane lessons): training loops run at no extra cost.
            sys.settrace(watcher.trace if trace else None)
            try:
                exec(compiled, namespace)
            finally:
                sys.settrace(previous_trace)
                if trace:
                    watcher.flush()
                reporter.flush()
    except KeyboardInterrupt:
        raise
    except MemoryError:
        raise UserCodeError(t("run.memory"), watcher.current_line, stdout=printed()) from None
    except RecursionError:
        raise UserCodeError(t("run.recursion"), watcher.current_line, stdout=printed()) from None
    except Exception as exc:  # noqa: BLE001 - any student error becomes a diagnostic
        raise UserCodeError(_describe(exc), _user_line(exc) or watcher.current_line, stdout=printed()) from None
    except BaseException as exc:  # noqa: BLE001 - `raise SystemExit`, `exit()`: report it, do not let it end the worker
        line = _user_line(exc) or watcher.current_line
        raise UserCodeError(t("run.exit"), line, stdout=printed()) from None

    if not require_circuit and not watcher.seen:
        return Execution(
            circuit=None, lines=[], stdout=stdout.getvalue()[:MAX_STDOUT_CHARS], namespace=namespace,
            reports=reporter.series, setup_private=setup_private,
        )
    circuit, lines = _pick_main_circuit(namespace, watcher)
    return Execution(
        circuit=circuit,
        lines=lines,
        stdout=stdout.getvalue()[:MAX_STDOUT_CHARS],
        namespace=namespace,
        reports=reporter.series,
        setup_private=setup_private,
    )


RUN_SHOTS_SEED = 7


def _run_shots(circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]:
    """Available in the student's code: runs the circuit `shots` times and returns the
    counts, as a quantum computer would. The seed is fixed so that the
    result does not change on every keystroke."""
    from .simulator import sample_counts

    if not isinstance(circuit, QuantumCircuit):
        raise TypeError("run_shots(qc, shots): qc must be a QuantumCircuit")
    return sample_counts(circuit, shots, seed=RUN_SHOTS_SEED)["counts"]


def _pick_main_circuit(namespace: dict, watcher: _CircuitWatcher) -> tuple[QuantumCircuit, list[int]]:
    preferred = namespace.get("qc")
    if isinstance(preferred, QuantumCircuit):
        return preferred, watcher.seen[id(preferred)][1]
    if not watcher.seen:
        raise UserCodeError(t("run.no_circuit"), kind="no_circuit")
    # Without `qc`: uses the most recently created circuit.
    circuit, lines, _ = max(watcher.seen.values(), key=lambda entry: entry[2])
    return circuit, lines


def _user_line(exc: BaseException) -> int | None:
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == USER_FILENAME:
            line = frame.lineno
    return line


def _describe(exc: BaseException) -> str:
    text = str(exc).strip()
    name = type(exc).__name__
    return f"{name}: {text}" if text else name
