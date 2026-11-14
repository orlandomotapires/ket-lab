"""Executa o código do aluno uma única vez e registra, para cada instrução
adicionada a um QuantumCircuit, a linha de nível de módulo que a originou.

"Estado após a linha k" não é bem definido quando há laços ou funções, então
a unidade de passo é a *instrução*. Uma instrução emitida dentro de uma função
é atribuída à linha de nível de módulo que chamou essa função; dentro de um
`for`, à linha do corpo do laço.
"""

from __future__ import annotations

import contextlib
import io
import math
import sys
import time
import traceback
from dataclasses import dataclass, field

from qiskit import QuantumCircuit

from . import guard
from .i18n import t

USER_FILENAME = "<aluno>"
MAX_STDOUT_CHARS = 10_000


class UserCodeError(Exception):
    """Erro atribuível ao código do aluno, com a linha quando conhecida."""

    def __init__(self, message: str, line: int | None = None, kind: str = "runtime"):
        super().__init__(message)
        self.message = message
        self.line = line
        self.kind = kind


@dataclass
class Execution:
    circuit: QuantumCircuit | None  # None em código PennyLane
    lines: list[int]  # linha de origem de cada instrução de circuit.data
    stdout: str = ""
    namespace: dict = field(default_factory=dict)
    reports: dict[str, list[float]] = field(default_factory=dict)


MAX_REPORTS = 5_000
REPORT_INTERVAL_S = 0.1


class Reporter:
    """`report(...)` no código do aluno: registra métricas de um laço de treino.

    `report(custo)` grava a série "cost"; `report(cost=c, accuracy=a)` grava várias.
    Com `emit`, os valores novos saem em lotes enquanto o código ainda roda
    (no máximo a cada REPORT_INTERVAL_S), para a curva aparecer época a época.
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
    """Número real de um float, inteiro, escalar NumPy ou tensor PennyLane de um elemento."""
    import numpy as np

    try:
        array = np.real(np.asarray(value, dtype=complex)).reshape(-1)
    except (TypeError, ValueError):
        return None
    if array.size != 1 or not np.isfinite(array[0]):
        return None
    return float(array[0])


class _CircuitWatcher:
    """Observa os QuantumCircuits do namespace e atribui linhas às instruções novas."""

    def __init__(self, namespace: dict):
        self.namespace = namespace
        self.current_line: int | None = None
        # id -> (circuito, linhas, ordem de criação). Guardar o circuito evita reuso de id.
        self.seen: dict[int, tuple[QuantumCircuit, list[int], int]] = {}

    def flush(self) -> None:
        line = self.current_line or 0
        for value in list(self.namespace.values()):
            if not isinstance(value, QuantumCircuit):
                continue
            entry = self.seen.get(id(value))
            if entry is None:
                entry = (value, [], len(self.seen))
                self.seen[id(value)] = entry
            lines = entry[1]
            count = len(value.data)
            if count > len(lines):
                lines.extend([line] * (count - len(lines)))
            elif count < len(lines):
                del lines[count:]

    def trace(self, frame, event, arg):
        code = frame.f_code
        if code.co_filename != USER_FILENAME or code.co_name != "<module>":
            return None
        return self._trace_module

    def _trace_module(self, frame, event, arg):
        if event == "line":
            self.flush()
            self.current_line = frame.f_lineno
        return self._trace_module


def execute(
    code: str,
    hidden_setup: str | None = None,
    inputs: dict | None = None,
    *,
    trace: bool = True,
    require_circuit: bool = True,
    reporter: Reporter | None = None,
) -> Execution:
    """Roda o código e devolve o circuito principal com a linha de cada instrução.

    `inputs` são variáveis colocadas no namespace antes do setup oculto: é assim
    que o validador varia, por exemplo, o estado que Alice teletransporta.
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
    if inputs:
        namespace.update(inputs)
    if hidden_setup:
        exec(compile(hidden_setup, "<setup>", "exec"), namespace)  # conteúdo da lição, confiável

    watcher = _CircuitWatcher(namespace)
    stdout = io.StringIO()
    compiled = compile(tree, USER_FILENAME, "exec")

    previous_trace = sys.gettrace()
    try:
        with contextlib.redirect_stdout(stdout):
            # Sem rastreamento (lições PennyLane): laços de treino rodam sem custo extra.
            sys.settrace(watcher.trace if trace else None)
            try:
                exec(compiled, namespace)
            finally:
                sys.settrace(previous_trace)
                if trace:
                    watcher.flush()
                reporter.flush()
    except MemoryError:
        raise UserCodeError(t("run.memory"), watcher.current_line) from None
    except RecursionError:
        raise UserCodeError(t("run.recursion"), watcher.current_line) from None
    except Exception as exc:  # noqa: BLE001 - qualquer erro do aluno vira diagnóstico
        raise UserCodeError(_describe(exc), _user_line(exc) or watcher.current_line) from None

    if not require_circuit and not watcher.seen:
        return Execution(
            circuit=None, lines=[], stdout=stdout.getvalue()[:MAX_STDOUT_CHARS], namespace=namespace,
            reports=reporter.series,
        )
    circuit, lines = _pick_main_circuit(namespace, watcher)
    return Execution(
        circuit=circuit,
        lines=lines,
        stdout=stdout.getvalue()[:MAX_STDOUT_CHARS],
        namespace=namespace,
        reports=reporter.series,
    )


RUN_SHOTS_SEED = 7


def _run_shots(circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]:
    """Disponível no código do aluno: executa o circuito `shots` vezes e devolve as
    contagens, como faria um computador quântico. A seed é fixa para que o
    resultado não mude a cada tecla."""
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
    # Sem `qc`: usa o circuito criado por último.
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
