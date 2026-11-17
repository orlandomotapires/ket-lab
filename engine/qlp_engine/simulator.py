"""Step-by-step state-vector simulator, with measurement and classical control.

Ordering convention (the same as Qiskit's, little-endian): qubit 0 is the
LEAST significant bit. Index i of the state vector is sum(b_q * 2**q), and the
label |q_{n-1} ... q_1 q_0> is the binary representation of i.

Measurements draw ONE branch with a seeded generator: the same seed reproduces the same
trajectory. For statistics use `sample_counts`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ClassicalRegister, Clbit, Gate
from qiskit.quantum_info import Operator

from .messages import t

DEFAULT_MAX_QUBITS = 10
MAX_INSTRUCTIONS = 2000
MAX_SHOTS = 8192


class SimulationError(Exception):
    """Circuit the simulator does not accept (with a message for the student)."""

    def __init__(self, message: str, line: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line


@dataclass
class Op:
    kind: str  # gate | channel | measure | reset | noop | conditional
    name: str
    qubits: tuple[int, ...] = ()
    clbits: tuple[int, ...] = ()
    matrix: np.ndarray | None = None
    params: tuple[float, ...] = ()
    num_ctrl: int = 0
    base: str | None = None  # name of the base gate, for controlled gates
    kraus: list[np.ndarray] = field(default_factory=list)  # noise channels
    # conditional:
    condition: tuple[tuple[int, ...], int] | None = None  # (clbits, expected value)
    body: list["Op"] = field(default_factory=list)
    else_body: list["Op"] = field(default_factory=list)


@dataclass
class StepRecord:
    op: Op
    line: int
    outcome: int | None = None  # drawn outcome (measure)
    applied: bool | None = None  # branch taken (conditional)


@dataclass
class Trajectory:
    num_qubits: int
    num_clbits: int
    steps: list[StepRecord]
    # states[0] = initial; states[k] = after step k. State vectors, or
    # density matrices when the circuit has noise channels.
    states: list[np.ndarray]
    clbits: list[int]


# --------------------------------------------------------------------------- #
# Compilation: QuantumCircuit -> list of Op with ready-made matrices
# --------------------------------------------------------------------------- #


def compile_circuit(circuit: QuantumCircuit, max_qubits: int = DEFAULT_MAX_QUBITS) -> list[Op]:
    if circuit.num_qubits == 0:
        raise SimulationError(t("sim.no_qubits"))
    if circuit.num_qubits > max_qubits:
        raise SimulationError(t("sim.too_many_qubits", count=circuit.num_qubits, limit=max_qubits))
    if len(circuit.data) > MAX_INSTRUCTIONS:
        raise SimulationError(t("sim.too_many_instructions", count=len(circuit.data), limit=MAX_INSTRUCTIONS))
    qubit_index = {bit: i for i, bit in enumerate(circuit.qubits)}
    clbit_index = {bit: i for i, bit in enumerate(circuit.clbits)}
    return _compile(circuit, qubit_index, clbit_index)


def _compile(circuit: QuantumCircuit, qmap: dict, cmap: dict) -> list[Op]:
    ops: list[Op] = []
    for instruction in circuit.data:
        operation = instruction.operation
        name = operation.name
        qubits = tuple(qmap[q] for q in instruction.qubits)
        clbits = tuple(cmap[c] for c in instruction.clbits)

        if name in ("barrier", "delay"):
            ops.append(Op("noop", name, qubits))
        elif name == "measure":
            ops.append(Op("measure", name, qubits, clbits))
        elif name == "reset":
            ops.append(Op("reset", name, qubits))
        elif name == "if_else":
            ops.append(_compile_conditional(instruction, qubits, clbits, cmap))
        elif name in ("for_loop", "while_loop", "switch_case", "box", "break_loop", "continue_loop"):
            raise SimulationError(t("sim.control_flow", name=name))
        elif isinstance(operation, Gate):
            ops.append(
                Op(
                    "gate",
                    name,
                    qubits,
                    matrix=_matrix_of(operation),
                    params=_float_params(operation),
                    num_ctrl=int(getattr(operation, "num_ctrl_qubits", 0) or 0),
                    base=getattr(getattr(operation, "base_gate", None), "name", None),
                )
            )
        elif operation.definition is not None:
            # Non-unitary composite instruction (e.g. initialize): expand the definition.
            inner = operation.definition
            inner_q = {bit: qubits[i] for i, bit in enumerate(inner.qubits)}
            inner_c = {bit: clbits[i] for i, bit in enumerate(inner.clbits)}
            body = _compile(inner, inner_q, inner_c)
            ops.append(Op("conditional", name, qubits, clbits, condition=None, body=body))
        else:
            raise SimulationError(t("sim.unsupported", name=name))
    return ops


def _compile_conditional(instruction, qubits, clbits, cmap) -> Op:
    operation = instruction.operation
    condition = operation.condition
    if not isinstance(condition, tuple):
        raise SimulationError(t("sim.expr_condition"))
    target, value = condition
    if isinstance(target, Clbit):
        cond_bits: tuple[int, ...] = (cmap[target],)
    elif isinstance(target, ClassicalRegister):
        cond_bits = tuple(cmap[bit] for bit in target)
    else:
        raise SimulationError(t("sim.bad_condition"))

    bodies = []
    for block in operation.blocks:
        inner_q = {bit: qubits[i] for i, bit in enumerate(block.qubits)}
        inner_c = {bit: clbits[i] for i, bit in enumerate(block.clbits)}
        bodies.append(_compile(block, inner_q, inner_c))
    return Op(
        "conditional",
        "if_else",
        qubits,
        clbits,
        condition=(cond_bits, int(value)),
        body=bodies[0] if bodies else [],
        else_body=bodies[1] if len(bodies) > 1 else [],
    )


def _matrix_of(operation: Gate) -> np.ndarray:
    try:
        matrix = operation.to_matrix()
    except Exception:  # noqa: BLE001 - gates without a direct to_matrix
        matrix = None
    if matrix is None:
        try:
            matrix = Operator(operation).data
        except Exception as exc:  # noqa: BLE001
            raise SimulationError(t("sim.no_matrix", name=operation.name)) from exc
    return np.asarray(matrix, dtype=complex)


def _float_params(operation) -> tuple[float, ...]:
    values = []
    for param in operation.params:
        try:
            values.append(float(param))
        except (TypeError, ValueError):
            return ()
    return tuple(values)


# --------------------------------------------------------------------------- #
# Numerical core
# --------------------------------------------------------------------------- #


def initial_state(num_qubits: int) -> np.ndarray:
    state = np.zeros(2**num_qubits, dtype=complex)
    state[0] = 1.0
    return state


def apply_matrix(state: np.ndarray, matrix: np.ndarray, qubits: tuple[int, ...], n: int) -> np.ndarray:
    """Applies a 2^k x 2^k matrix to the given qubits (qubits[0] = least significant bit)."""
    k = len(qubits)
    tensor = state.reshape((2,) * n)
    gate = matrix.reshape((2,) * (2 * k))
    # Tensor axis for qubit q: n-1-q. The matrix indexes (q_{k-1} ... q_0).
    axes = [n - 1 - q for q in reversed(qubits)]
    result = np.tensordot(gate, tensor, axes=(list(range(k, 2 * k)), axes))
    result = np.moveaxis(result, list(range(k)), axes)
    return np.ascontiguousarray(result).reshape(-1)


def _measure(state: np.ndarray, qubit: int, n: int, rng: np.random.Generator) -> tuple[int, np.ndarray]:
    tensor = state.reshape((2,) * n)
    axis = n - 1 - qubit
    p1 = float(np.sum(np.abs(np.take(tensor, 1, axis=axis)) ** 2))
    outcome = 1 if rng.random() < p1 else 0
    collapsed = np.zeros_like(tensor)
    index = [slice(None)] * n
    index[axis] = outcome
    collapsed[tuple(index)] = tensor[tuple(index)]
    norm = math.sqrt(p1 if outcome else 1.0 - p1)
    return outcome, (collapsed / norm).reshape(-1)


_X = np.array([[0, 1], [1, 0]], dtype=complex)


def _run_ops(
    ops: list[Op],
    state: np.ndarray,
    clbits: list[int],
    n: int,
    rng: np.random.Generator,
    record: list[StepRecord] | None = None,
    states: list[np.ndarray] | None = None,
    lines: list[int] | None = None,
    observer=None,
) -> np.ndarray:
    for position, op in enumerate(ops):
        outcome = None
        applied = None
        if op.kind == "gate":
            state = apply_matrix(state, op.matrix, op.qubits, n)
        elif op.kind == "measure":
            outcome, state = _measure(state, op.qubits[0], n, rng)
            clbits[op.clbits[0]] = outcome
        elif op.kind == "reset":
            for qubit in op.qubits:
                bit, state = _measure(state, qubit, n, rng)
                if bit:
                    state = apply_matrix(state, _X, (qubit,), n)
        elif op.kind == "conditional":
            if op.condition is None:
                applied = True
            else:
                bits, expected = op.condition
                actual = sum(clbits[b] << i for i, b in enumerate(bits))
                applied = actual == expected
            branch = op.body if applied else op.else_body
            state = _run_ops(branch, state, clbits, n, rng)
        if record is not None:
            record.append(StepRecord(op, lines[position] if lines else 0, outcome, applied))
            if observer is None:
                states.append(state)
            else:
                states.append(None)  # the observer already took what it needs from this state
                observer.add(state)
    return state


MAX_DENSITY_QUBITS = 8


def apply_to_density(rho: np.ndarray, matrices: list[np.ndarray], qubits: tuple[int, ...], n: int) -> np.ndarray:
    """ρ -> Σ K ρ K†. A gate is the case of a single K (unitary).

    ρ is treated as a vector of 2n qubits: the n high bits index the row and the n
    low bits the column; K acts on the rows and K* on the columns.
    """
    vector = rho.reshape(-1)
    rows = tuple(q + n for q in qubits)
    result = np.zeros_like(vector)
    for k in matrices:
        part = apply_matrix(vector, k, rows, 2 * n)
        result += apply_matrix(part, k.conj(), qubits, 2 * n)
    return result.reshape(2**n, 2**n)


class FinalOnly:
    """Observer that wants no per-step data: `Trajectory.states` keeps only the final state."""

    def begin(self, num_qubits: int, total: int) -> None:
        pass

    def add(self, state: np.ndarray) -> None:
        pass


def _run_density(ops: list[Op], n: int, lines: list[int], observer=None) -> tuple[list[StepRecord], list[np.ndarray]]:
    if n > MAX_DENSITY_QUBITS:
        raise SimulationError(t("sim.too_many_qubits", count=n, limit=MAX_DENSITY_QUBITS))
    rho = np.zeros((2**n, 2**n), dtype=complex)
    rho[0, 0] = 1.0
    steps: list[StepRecord] = []
    states = [rho if observer is None else None]
    if observer is not None:
        observer.begin(n, len(ops) + 1)
        observer.add(rho)
    for position, op in enumerate(ops):
        if op.kind == "gate":
            rho = apply_to_density(rho, [op.matrix], op.qubits, n)
        elif op.kind == "channel":
            rho = apply_to_density(rho, op.kraus, op.qubits, n)
        elif op.kind != "noop":
            raise SimulationError(t("sim.unsupported", name=op.name))
        steps.append(StepRecord(op, lines[position]))
        states.append(rho if observer is None else None)
        if observer is not None:
            observer.add(rho)
    if observer is not None:
        states[-1] = rho  # the last state is always kept (the shots job and the validators read it)
    return steps, states


def run_ops_trajectory(
    ops: list[Op],
    lines: list[int],
    num_qubits: int,
    seed: int = 0,
    max_qubits: int = DEFAULT_MAX_QUBITS,
    observer=None,
) -> Trajectory:
    """Simulates already-compiled operations (e.g. coming from a PennyLane circuit).

    With noise channels, the simulation uses a density matrix. With an `observer` (begin(n, total) and
    add(state), see geometry.SnapshotCollector) the states are handed over one by one and not kept,
    except the last one: a long circuit then needs memory for one state, not one per step.
    """
    if num_qubits == 0:
        raise SimulationError(t("sim.no_qubits"))
    if num_qubits > max_qubits:
        raise SimulationError(t("sim.too_many_qubits", count=num_qubits, limit=max_qubits))
    if len(ops) > MAX_INSTRUCTIONS:
        raise SimulationError(t("sim.too_many_instructions", count=len(ops), limit=MAX_INSTRUCTIONS))
    if any(op.kind == "channel" for op in ops):
        steps, states = _run_density(ops, num_qubits, lines, observer)
        return Trajectory(num_qubits, 0, steps, states, [])
    state = initial_state(num_qubits)
    steps: list[StepRecord] = []
    states = _first_states(state, num_qubits, len(ops), observer)
    final = _run_ops(ops, state, [], num_qubits, np.random.default_rng(seed), steps, states, lines, observer)
    if observer is not None:
        states[-1] = final
    return Trajectory(num_qubits, 0, steps, states, [])


def _first_states(state: np.ndarray, n: int, count: int, observer) -> list:
    if observer is None:
        return [state]
    observer.begin(n, count + 1)
    observer.add(state)
    return [None]


def final_state(circuit: QuantumCircuit, seed: int = 0, max_qubits: int = DEFAULT_MAX_QUBITS) -> np.ndarray:
    """The state after the last instruction, without keeping the states in between."""
    return run_trajectory(circuit, seed=seed, max_qubits=max_qubits, observer=FinalOnly()).states[-1]


def state_probabilities(state: np.ndarray) -> np.ndarray:
    """Computational-basis probabilities, for a state vector or a density matrix."""
    if state.ndim == 2:
        return np.clip(np.real(np.diag(state)), 0.0, None)
    return np.abs(state) ** 2


def run_trajectory(
    circuit: QuantumCircuit,
    lines: list[int] | None = None,
    seed: int = 0,
    max_qubits: int = DEFAULT_MAX_QUBITS,
    observer=None,
) -> Trajectory:
    """Simulates one trajectory, keeping the state after each instruction (or handing it to `observer`)."""
    ops = compile_circuit(circuit, max_qubits)
    n = circuit.num_qubits
    rng = np.random.default_rng(seed)
    clbits = [0] * circuit.num_clbits
    state = initial_state(n)
    steps: list[StepRecord] = []
    states = _first_states(state, n, len(ops), observer)
    final = _run_ops(ops, state, clbits, n, rng, steps, states, lines or [0] * len(ops), observer)
    if observer is not None:
        states[-1] = final
    return Trajectory(n, circuit.num_clbits, steps, states, clbits)


# --------------------------------------------------------------------------- #
# Sampling (shots)
# --------------------------------------------------------------------------- #


def _has_measure(ops: list[Op]) -> bool:
    return any(
        op.kind == "measure" or (op.kind == "conditional" and _has_measure(op.body + op.else_body))
        for op in ops
    )


def _needs_trajectories(ops: list[Op]) -> bool:
    """True if anything beyond terminal measurements depends on the random draw."""
    seen_measure = False
    measured: set[int] = set()
    for op in ops:
        if op.kind in ("reset", "conditional"):
            return True
        if op.kind == "measure":
            if op.qubits[0] in measured:
                return True
            measured.add(op.qubits[0])
            seen_measure = True
        elif op.kind == "gate" and seen_measure:
            return True
    return False


def exact_distribution(circuit: QuantumCircuit, max_qubits: int = DEFAULT_MAX_QUBITS) -> dict[str, float] | None:
    """Exact probability of each classical outcome, or None if it depends on
    mid-circuit measurements (then only by sampling trajectories)."""
    ops = compile_circuit(circuit, max_qubits)
    if not _has_measure(ops) or _needs_trajectories(ops):
        return None
    n = circuit.num_qubits
    state = _run_ops([op for op in ops if op.kind == "gate"], initial_state(n), [], n, np.random.default_rng(0))
    mapping = [(op.qubits[0], op.clbits[0]) for op in ops if op.kind == "measure"]
    distribution: dict[str, float] = {}
    for index, probability in enumerate(np.abs(state) ** 2):
        if probability < 1e-12:
            continue
        value = 0
        for qubit, clbit in mapping:
            value |= ((index >> qubit) & 1) << clbit
        key = format(value, f"0{circuit.num_clbits}b")
        distribution[key] = distribution.get(key, 0.0) + float(probability)
    return dict(sorted(distribution.items()))


MAX_BRANCHES = 512


class _TooManyBranches(Exception):
    pass


def _advance(ops: list[Op], branches: list, n: int, limit: int) -> list:
    """Follows EVERY outcome of the measurements and resets in `ops`.

    A branch is (probability, state, classical bits). Each measurement splits a branch in two, so the
    count can double; past `limit` the caller gives up and samples instead.
    """
    for op in ops:
        following = []
        for weight, state, clbits in branches:
            if op.kind == "gate":
                following.append((weight, apply_matrix(state, op.matrix, op.qubits, n), clbits))
            elif op.kind in ("measure", "reset"):
                qubit = op.qubits[0]
                for outcome, probability, collapsed in _collapses(state, qubit, n):
                    bits = clbits
                    if op.kind == "measure":
                        bits = list(clbits)
                        bits[op.clbits[0]] = outcome
                    elif outcome:
                        collapsed = apply_matrix(collapsed, _X, (qubit,), n)
                    following.append((weight * probability, collapsed, bits))
            elif op.kind == "conditional":
                if op.condition is None:
                    taken = op.body
                else:
                    bits_wanted, expected = op.condition
                    taken = op.body if sum(clbits[b] << i for i, b in enumerate(bits_wanted)) == expected else op.else_body
                following.extend(_advance(taken, [(weight, state, clbits)], n, limit))
            else:  # noop
                following.append((weight, state, clbits))
        if len(following) > limit:
            raise _TooManyBranches
        branches = following
    return branches


def _collapses(state: np.ndarray, qubit: int, n: int):
    """(outcome, probability, collapsed state) for each outcome of measuring one qubit that can happen."""
    tensor = state.reshape((2,) * n)
    axis = n - 1 - qubit
    for outcome in (0, 1):
        index = [slice(None)] * n
        index[axis] = outcome
        part = tensor[tuple(index)]
        probability = float(np.sum(np.abs(part) ** 2))
        if probability < 1e-12:
            continue
        collapsed = np.zeros_like(tensor)
        collapsed[tuple(index)] = part
        yield outcome, probability, (collapsed / math.sqrt(probability)).reshape(-1)


def branching_distribution(circuit: QuantumCircuit, max_qubits: int = DEFAULT_MAX_QUBITS) -> dict[str, float] | None:
    """Exact probability of each classical outcome for a circuit with measurements (or resets, or
    classical control) in the middle, by following every branch; None when there are more than
    MAX_BRANCHES of them (then only sampling is left)."""
    ops = compile_circuit(circuit, max_qubits)
    n = circuit.num_qubits
    start = [(1.0, initial_state(n), [0] * circuit.num_clbits)]
    try:
        branches = _advance(ops, start, n, MAX_BRANCHES)
    except _TooManyBranches:
        return None
    distribution: dict[str, float] = {}
    for weight, _, clbits in branches:
        key = "".join(str(b) for b in reversed(clbits))
        distribution[key] = distribution.get(key, 0.0) + weight
    return dict(sorted((key, value) for key, value in distribution.items() if value > 1e-12))


def register_distribution(
    circuit: QuantumCircuit,
    register: list[int],
    max_qubits: int = DEFAULT_MAX_QUBITS,
) -> dict[str, float]:
    """Probability of each register value at the end (label |r_{k-1} … r_0⟩).

    Final measurements are ignored: what matters is the state right before them. With
    mid-circuit measurements, the average is taken over several trajectories.
    """
    ops = compile_circuit(circuit, max_qubits)
    n = circuit.num_qubits
    if _needs_trajectories(ops):
        states = [run_trajectory(circuit, seed=seed, max_qubits=max_qubits).states[-1] for seed in range(32)]
    else:
        states = [_run_ops([op for op in ops if op.kind == "gate"], initial_state(n), [], n, np.random.default_rng(0))]
    width = len(register)
    distribution: dict[str, float] = {}
    for state in states:
        for index, probability in enumerate(np.abs(state) ** 2):
            if probability < 1e-12:
                continue
            value = sum(((index >> qubit) & 1) << position for position, qubit in enumerate(register))
            key = format(value, f"0{width}b")
            distribution[key] = distribution.get(key, 0.0) + float(probability) / len(states)
    return dict(sorted(distribution.items()))


def sample_counts(
    circuit: QuantumCircuit,
    shots: int = 1024,
    seed: int = 0,
    max_qubits: int = DEFAULT_MAX_QUBITS,
) -> dict:
    """Simulates `shots` runs. With no measurements in the circuit, measures all qubits at the end."""
    shots = max(1, min(int(shots), MAX_SHOTS))
    ops = compile_circuit(circuit, max_qubits)
    n = circuit.num_qubits
    rng = np.random.default_rng(seed)
    has_measure = _has_measure(ops)
    width = circuit.num_clbits if has_measure else n
    counts: dict[str, int] = {}

    if has_measure and _needs_trajectories(ops):
        for _ in range(shots):
            clbits = [0] * circuit.num_clbits
            _run_ops(ops, initial_state(n), clbits, n, rng)
            key = "".join(str(b) for b in reversed(clbits))
            counts[key] = counts.get(key, 0) + 1
    else:
        # Measurements only at the end: just sample the state's distribution before them.
        unitary_ops = [op for op in ops if op.kind == "gate"]
        state = _run_ops(unitary_ops, initial_state(n), [], n, rng)
        probabilities = np.abs(state) ** 2
        probabilities /= probabilities.sum()
        samples = rng.choice(len(probabilities), size=shots, p=probabilities)
        mapping = [(op.qubits[0], op.clbits[0]) for op in ops if op.kind == "measure"]
        for sample in samples:
            if has_measure:
                value = 0
                for qubit, clbit in mapping:
                    value |= ((int(sample) >> qubit) & 1) << clbit
            else:
                value = int(sample)
            key = format(value, f"0{width}b")
            counts[key] = counts.get(key, 0) + 1

    return {
        "shots": shots,
        "counts": dict(sorted(counts.items())),
        "measured": "clbits" if has_measure else "qubits",
        "width": width,
    }
