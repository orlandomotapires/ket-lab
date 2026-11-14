"""Circuitos PennyLane no laboratório.

Executa a função de um QNode uma vez, gravando cada operação com a linha do
código do aluno que a criou, e converte tudo para as operações do simulador
(as mesmas usadas pelos circuitos Qiskit). Assim a linha do tempo, o diagrama e
as visualizações funcionam igual. Canais de ruído (BitFlip, DepolarizingChannel…)
viram operadores de Kraus e levam a simulação para matriz densidade.

Convenção: o fio (wire) de índice k no dispositivo é o qubit k da plataforma, e os
rótulos seguem a ordem do Qiskit (|q_{n-1} … q_0⟩), a mesma das outras trilhas.
"""

from __future__ import annotations

import sys

import numpy as np

from .i18n import t
from .simulator import Op
from .tracer import USER_FILENAME, UserCodeError

MAX_EXPANSION_DEPTH = 8

# nome PennyLane -> (nome na plataforma, nº de controles, porta base)
NAMES: dict[str, tuple[str, int, str | None]] = {
    "PauliX": ("x", 0, None),
    "PauliY": ("y", 0, None),
    "PauliZ": ("z", 0, None),
    "Hadamard": ("h", 0, None),
    "S": ("s", 0, None),
    "T": ("t", 0, None),
    "SX": ("sx", 0, None),
    "RX": ("rx", 0, None),
    "RY": ("ry", 0, None),
    "RZ": ("rz", 0, None),
    "PhaseShift": ("p", 0, None),
    "Rot": ("rot", 0, None),
    "U3": ("u", 0, None),
    "CNOT": ("cx", 1, "x"),
    "CY": ("cy", 1, "y"),
    "CZ": ("cz", 1, "z"),
    "CH": ("ch", 1, "h"),
    "CRX": ("crx", 1, "rx"),
    "CRY": ("cry", 1, "ry"),
    "CRZ": ("crz", 1, "rz"),
    "ControlledPhaseShift": ("cp", 1, "p"),
    "Toffoli": ("ccx", 2, "x"),
    "SWAP": ("swap", 0, None),
    "IsingZZ": ("rzz", 0, None),
    "MultiRZ": ("rzz", 0, None),
    "Identity": ("id", 0, None),
    "Adjoint(S)": ("sdg", 0, None),
    "Adjoint(T)": ("tdg", 0, None),
    "QubitChannel": ("kraus", 0, None),
    # Excitações da química: mantidas como uma porta só (decompostas, viram dezenas de portas).
    "SingleExcitation": ("singleexcitation", 0, None),
    "DoubleExcitation": ("doubleexcitation", 0, None),
    "BitFlip": ("bitflip", 0, None),
    "PhaseFlip": ("phaseflip", 0, None),
    "DepolarizingChannel": ("depolarizing", 0, None),
    "AmplitudeDamping": ("amplitudedamping", 0, None),
    "PhaseDamping": ("phasedamping", 0, None),
}


def is_qnode(value) -> bool:
    import pennylane as qml

    return isinstance(value, qml.QNode)


def find_qnode(namespace: dict, name: str | None = None):
    """O QNode indicado pela lição, ou o último definido no código."""
    if name and is_qnode(namespace.get(name)):
        return namespace[name]
    qnodes = [value for key, value in namespace.items() if not key.startswith("_") and is_qnode(value)]
    if not qnodes:
        raise UserCodeError(t("pl.no_qnode"), kind="no_circuit")
    return qnodes[-1]


def qnode_arguments(qnode, namespace: dict, names: list[str] | None) -> list:
    """Argumentos para desenhar o circuito: variáveis do código do aluno (ex.: os parâmetros treinados)."""
    values = []
    for name in names or []:
        if name not in namespace:
            raise UserCodeError(t("pl.missing_argument", name=name), kind="runtime")
        values.append(namespace[name])
    return values


def trace_qnode(qnode, args: list) -> tuple[list[Op], list[int], int]:
    """Executa a função do QNode uma vez e devolve (operações, linhas, nº de qubits)."""
    import pennylane as qml
    from pennylane.measurements import MeasurementProcess
    from pennylane.queuing import AnnotatedQueue

    wires = list(qnode.device.wires)
    index = {wire: position for position, wire in enumerate(wires)}
    current_line = [0]
    line_of: dict[int, int] = {}

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != USER_FILENAME:
            return None
        if event == "line":
            current_line[0] = frame.f_lineno
        return tracer

    original_append = AnnotatedQueue.append

    def recording_append(self, obj, **kwargs):
        line_of.setdefault(id(obj), current_line[0])
        return original_append(self, obj, **kwargs)

    queue = AnnotatedQueue()
    previous = sys.gettrace()
    AnnotatedQueue.append = recording_append
    try:
        with queue:
            sys.settrace(tracer)
            try:
                qnode.func(*args)
            finally:
                sys.settrace(previous)
    except UserCodeError:
        raise
    except Exception as exc:  # noqa: BLE001 - erro no corpo do QNode
        from .tracer import _describe, _user_line

        raise UserCodeError(_describe(exc), _user_line(exc)) from None
    finally:
        AnnotatedQueue.append = original_append

    ops: list[Op] = []
    lines: list[int] = []
    for obj in queue.queue:
        if isinstance(obj, MeasurementProcess) or not isinstance(obj, qml.operation.Operator):
            continue
        line = line_of.get(id(obj), 0)
        try:
            for op in _expand(obj, 0):
                ops.append(_convert(op, index))
                lines.append(line)
        except UserCodeError as exc:
            exc.line = exc.line or line or None
            raise
    return ops, lines, len(wires)


def _expand(op, depth: int) -> list:
    """Decompõe templates (AngleEmbedding, camadas…) até portas conhecidas."""
    import pennylane as qml

    if op.name in NAMES or isinstance(op, qml.operation.Channel) or depth >= MAX_EXPANSION_DEPTH:
        return [op]
    if op.name in ("MidMeasureMP", "Conditional"):
        raise UserCodeError(t("pl.unsupported", name=op.name), kind="runtime")
    try:
        parts = op.decomposition()
    except Exception:  # noqa: BLE001 - sem decomposição: usa a matriz inteira
        return [op]
    return [leaf for part in parts for leaf in _expand(part, depth + 1)]


def _convert(op, index: dict) -> Op:
    import pennylane as qml

    try:
        qubits = tuple(index[wire] for wire in op.wires)
    except KeyError as exc:
        raise UserCodeError(t("pl.unknown_wire", wire=exc.args[0]), kind="runtime") from None
    name, num_ctrl, base = NAMES.get(op.name, (op.name, 0, None))
    # Com broadcasting (lote de 1 exemplo), parâmetros chegam como arrays de tamanho 1.
    params = tuple(_scalar(p) for p in op.parameters if np.size(p) == 1)
    k = len(qubits)
    if isinstance(op, qml.operation.Channel):
        kraus = [_little_endian(np.asarray(m, dtype=complex), k) for m in op.kraus_matrices()]
        return Op("channel", name, qubits, params=params, kraus=kraus)
    try:
        matrix = np.asarray(qml.matrix(op), dtype=complex)
    except Exception:  # noqa: BLE001
        raise UserCodeError(t("pl.unsupported", name=op.name), kind="runtime") from None
    if matrix.ndim == 3:  # broadcasting: desenha o primeiro exemplo do lote
        matrix = matrix[0]
    return Op("gate", name, qubits, matrix=_little_endian(matrix, k), params=params, num_ctrl=num_ctrl, base=base)


def _little_endian(matrix: np.ndarray, k: int) -> np.ndarray:
    """PennyLane indexa a matriz com o primeiro fio como bit mais significativo; o
    simulador espera o primeiro qubit da lista como o menos significativo."""
    if k == 1:
        return matrix
    tensor = matrix.reshape((2,) * (2 * k))
    axes = list(range(k))[::-1] + list(range(k, 2 * k))[::-1]
    return tensor.transpose(axes).reshape(2**k, 2**k)


def _scalar(value) -> float:
    try:
        return float(np.real(np.asarray(value).reshape(-1)[0]))
    except (TypeError, ValueError):
        return 0.0
