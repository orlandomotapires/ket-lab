"""PennyLane circuits in the lab.

Runs a QNode's function once, recording each operation with the line of the
student's code that created it, and converts everything to the simulator's operations
(the same ones used by Qiskit circuits). This way the timeline, the diagram and
the visualizations work the same way. Noise channels (BitFlip, DepolarizingChannel…)
become Kraus operators and move the simulation to density matrices.

Convention: the wire of index k on the device is the platform's qubit k, and the
labels follow Qiskit's order (|q_{n-1} … q_0⟩), the same as in the other tracks.
"""

from __future__ import annotations

import sys

import numpy as np

from .messages import t
from .simulator import Op
from .tracer import USER_FILENAME, UserCodeError

MAX_EXPANSION_DEPTH = 8

# PennyLane name -> (platform name, number of controls, base gate)
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
    # Chemistry excitations: kept as a single gate (decomposed, they become dozens of gates).
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
    """The QNode named by the lesson, or the last one defined in the code."""
    if name and is_qnode(namespace.get(name)):
        return namespace[name]
    qnodes = [value for key, value in namespace.items() if not key.startswith("_") and is_qnode(value)]
    if not qnodes:
        raise UserCodeError(t("pl.no_qnode"), kind="no_circuit")
    return qnodes[-1]


def qnode_arguments(qnode, namespace: dict, names: list[str] | None) -> list:
    """Arguments for drawing the circuit: variables from the student's code (e.g. the trained parameters)."""
    if names is None:
        names = required_parameters(qnode)
    values = []
    for name in names:
        if name not in namespace:
            raise UserCodeError(t("pl.missing_argument", name=name), kind="runtime")
        values.append(namespace[name])
    return values


def required_parameters(qnode) -> list[str]:
    """Parameters without a default value of the QNode function: in the free lab, `circuit(params)`
    is drawn with the code's `params` variable, if it exists."""
    import inspect

    try:
        signature = inspect.signature(qnode.func)
    except (TypeError, ValueError):
        return []
    return [
        p.name for p in signature.parameters.values()
        if p.default is inspect.Parameter.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]


def trace_qnode(qnode, args: list) -> tuple[list[Op], list[int], int]:
    """Runs the QNode function once and returns (operations, lines, number of qubits)."""
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
    except Exception as exc:  # noqa: BLE001 - error in the QNode body
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
    """Decomposes templates (AngleEmbedding, layers…) down to known gates."""
    import pennylane as qml

    if op.name in NAMES or isinstance(op, qml.operation.Channel) or depth >= MAX_EXPANSION_DEPTH:
        return [op]
    if op.name in ("MidMeasureMP", "Conditional"):
        raise UserCodeError(t("pl.unsupported", name=op.name), kind="runtime")
    try:
        parts = op.decomposition()
    except Exception:  # noqa: BLE001 - no decomposition: use the whole matrix
        return [op]
    return [leaf for part in parts for leaf in _expand(part, depth + 1)]


def _convert(op, index: dict) -> Op:
    import pennylane as qml

    try:
        qubits = tuple(index[wire] for wire in op.wires)
    except KeyError as exc:
        raise UserCodeError(t("pl.unknown_wire", wire=exc.args[0]), kind="runtime") from None
    name, num_ctrl, base = NAMES.get(op.name, (op.name, 0, None))
    # With broadcasting (batch of 1 example), parameters arrive as arrays of size 1.
    params = tuple(_scalar(p) for p in op.parameters if np.size(p) == 1)
    k = len(qubits)
    if isinstance(op, qml.operation.Channel):
        kraus = [_little_endian(np.asarray(m, dtype=complex), k) for m in op.kraus_matrices()]
        return Op("channel", name, qubits, params=params, kraus=kraus)
    try:
        matrix = np.asarray(qml.matrix(op), dtype=complex)
    except Exception:  # noqa: BLE001
        raise UserCodeError(t("pl.unsupported", name=op.name), kind="runtime") from None
    if matrix.ndim == 3:  # broadcasting: draw the first example of the batch
        matrix = matrix[0]
    return Op("gate", name, qubits, matrix=_little_endian(matrix, k), params=params, num_ctrl=num_ctrl, base=base)


def _little_endian(matrix: np.ndarray, k: int) -> np.ndarray:
    """PennyLane indexes the matrix with the first wire as the most significant bit; the
    simulator expects the first qubit in the list to be the least significant."""
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
