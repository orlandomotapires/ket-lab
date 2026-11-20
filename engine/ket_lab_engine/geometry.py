"""Translation of the state vector into quantities ready for rendering."""

from __future__ import annotations

import math

import numpy as np

from .messages import t
from .simulator import Op, StepRecord, Trajectory

DECIMALS = 6
# A reply keeps full per-step data (amplitudes and probabilities, about 2^n numbers each) for at most
# this many steps x 2^n; a 10-qubit circuit then has about 146 full snapshots (around 3 MB of JSON)
# instead of one per instruction (50 MB for 1,500 gates). Every step keeps its Bloch vectors.
MAX_FULL_ELEMENTS = 150_000
MIN_FULL_SNAPSHOTS = 24


def reduced_density(state: np.ndarray, n: int, qubit: int) -> np.ndarray:
    """2x2 density matrix of one qubit, from a state vector or a density matrix."""
    if state.ndim == 2:
        tensor = state.reshape((2,) * (2 * n))
        row, col = n - 1 - qubit, 2 * n - 1 - qubit
        moved = np.moveaxis(tensor, (row, col), (0, n))
        return np.einsum("ajbj->ab", moved.reshape(2, 2 ** (n - 1), 2, 2 ** (n - 1)))
    m = np.moveaxis(state.reshape((2,) * n), n - 1 - qubit, 0).reshape(2, -1)
    return m @ m.conj().T


def bloch_vectors(state: np.ndarray, n: int) -> tuple[list[list[float]], list[float]]:
    """Bloch vector (x, y, z) and purity Tr(rho^2) of each qubit's reduced state.

    An entangled qubit, or one subject to noise, has a mixed local state: the vector shrinks (|r| < 1).
    """
    vectors: list[list[float]] = []
    purities: list[float] = []
    for qubit in range(n):
        rho = reduced_density(state, n, qubit)
        x = 2.0 * rho[0, 1].real
        y = -2.0 * rho[0, 1].imag
        z = (rho[0, 0] - rho[1, 1]).real
        vectors.append([round(float(v), DECIMALS) for v in (x, y, z)])
        purities.append(round(float(np.real(np.trace(rho @ rho))), DECIMALS))
    return vectors, purities


def snapshot(state: np.ndarray, n: int, full: bool = True) -> dict:
    """State ready for the interface. Mixed states have no amplitudes (`None`).

    With `full=False` (a long run over budget) the two lists that grow with 2^n are left out:
    `amplitudes` is `None` and `probabilities` is empty, and the snapshot says `"reduced": true`.
    The Bloch vectors and purities, which the interface needs for every step, stay.
    """
    vectors, purities = bloch_vectors(state, n)
    if state.ndim == 2:
        # Tr(rho^2) = sum |rho_ij|^2 for a Hermitian matrix, without the O(8^n) matrix product.
        total_purity = float(np.sum(np.abs(state) ** 2))
    else:
        total_purity = 1.0
    light = {
        "bloch": vectors,
        "purity": purities,
        "state_purity": round(total_purity, DECIMALS),
    }
    if not full:
        return {"amplitudes": None, "probabilities": [], **light, "reduced": True}
    if state.ndim == 2:
        probabilities = np.clip(np.real(np.diag(state)), 0.0, None)
        amplitudes = None
    else:
        probabilities = np.abs(state) ** 2
        rounded = np.round(state, DECIMALS)
        amplitudes = [[float(a.real), float(a.imag)] for a in rounded]
    return {
        "amplitudes": amplitudes,
        "probabilities": [round(float(p), DECIMALS) for p in probabilities],
        **light,
    }


class SnapshotCollector:
    """Turns each state into a snapshot as the simulator produces it, within the reply budget.

    Handed to the simulator as its `observer`: states are not kept, so a long circuit (or a noisy one,
    whose states are 4^n numbers) never holds more than one in memory. Snapshots beyond the budget are
    reduced to their light data, except for evenly spaced ones and the last.
    """

    def __init__(self, budget: int = MAX_FULL_ELEMENTS):
        self.budget = budget
        self.num_qubits = 0
        self.total = 0
        self.full: set[int] = set()
        self.snapshots: list[dict] = []

    def begin(self, num_qubits: int, total: int) -> None:
        self.num_qubits, self.total = num_qubits, total
        allowed = max(MIN_FULL_SNAPSHOTS, self.budget >> num_qubits)
        self.full = set(range(total)) if total <= allowed else evenly_spaced(total, allowed)
        self.snapshots = []

    @property
    def truncated(self) -> bool:
        return len(self.full) < self.total

    def add(self, state: np.ndarray) -> None:
        self.snapshots.append(snapshot(state, self.num_qubits, full=len(self.snapshots) in self.full))


def evenly_spaced(total: int, count: int) -> set[int]:
    """`count` indices out of range(total), evenly spaced, always including the first and the last."""
    if count >= total:
        return set(range(total))
    if count <= 1:
        return {total - 1}
    return {round(i * (total - 1) / (count - 1)) for i in range(count)}


def describe_step(index: int, record: StepRecord) -> dict:
    op = record.op
    return {
        "index": index,
        "line": record.line,
        "kind": op.kind,
        "name": op.name,
        "label": _label(op),
        "qubits": list(op.qubits),
        "clbits": list(op.clbits),
        "num_ctrl": op.num_ctrl,
        "outcome": record.outcome,
        "applied": record.applied,
    }


def describe_trajectory(trajectory: Trajectory, collector: SnapshotCollector | None = None) -> dict:
    """The reply of a run. With a `collector` (the simulator's observer) the snapshots are already made.

    When the run is over budget the reply also carries `"truncated": true`, `"full_snapshots"` (the
    indices of the snapshots that kept their amplitudes and probabilities; 0 is the initial state and
    k the state after step k) and a `"notice"` for the learner. Otherwise those fields are absent.
    """
    n = trajectory.num_qubits
    if collector is None:
        collector = SnapshotCollector()
        collector.begin(n, len(trajectory.states))
        for state in trajectory.states:
            assert state is not None  # without an observer every state is kept
            collector.add(state)
    reply = {
        "num_qubits": n,
        "num_clbits": trajectory.num_clbits,
        "steps": [describe_step(i, record) for i, record in enumerate(trajectory.steps)],
        "snapshots": collector.snapshots,
        "clbits": trajectory.clbits,
        "has_measurement": any(r.outcome is not None for r in trajectory.steps),
    }
    if collector.truncated:
        reply["truncated"] = True
        reply["full_snapshots"] = sorted(collector.full)
        reply["notice"] = t("run.reduced", steps=len(trajectory.steps), qubits=n, kept=len(collector.full))
    return reply


_NAMES = {
    "id": "I",
    "sdg": "S†",
    "tdg": "T†",
    "sx": "√X",
    "sxdg": "√X†",
    "cx": "X",
    "cy": "Y",
    "cz": "Z",
    "ch": "H",
    "ccx": "X",
    "cp": "P",
    "crx": "RX",
    "cry": "RY",
    "crz": "RZ",
    "cswap": "SWAP",
    "measure": "M",
    "reset": "|0⟩",
    "if_else": "if",
    "initialize": "init",
    "psi": "ψ",
    "oracle": "U_f",
    "grover_oracle": "U_ω",
    "prepare_input": "|x⟩",
    "qft_dagger": "QFT†",
    "mcx": "X",
    "ccz": "Z",
    "mcp": "P",
    "rzz": "RZZ",
    "singleexcitation": "G",
    "doubleexcitation": "G²",
    "rot": "Rot",
    "kraus": "E",
    "bitflip": "BitFlip",
    "phaseflip": "PhaseFlip",
    "depolarizing": "Dep",
    "amplitudedamping": "AmpDamp",
    "phasedamping": "PhaseDamp",
}


def _label(op: Op) -> str:
    name = op.base if op.num_ctrl and op.base and op.name not in _NAMES else op.name
    # Names that are not identifiers ("U^4", "×7^2") are shown as they are.
    base = _NAMES.get(name) or (name.upper() if name.isidentifier() else name)
    if op.kind == "conditional" and op.condition is not None:
        bits, value = op.condition
        inner = " ".join(_label(child) for child in op.body) or "…"
        target = f"c{bits[0]}" if len(bits) == 1 else "c"
        return f"{inner} if {target}={value}"
    if op.params:
        return f"{base}({', '.join(format_angle(p) for p in op.params)})"
    return base


def format_angle(value: float) -> str:
    """Writes angles as fractions of π when possible (e.g. π/2, 3π/4)."""
    if abs(value) < 1e-9:
        return "0"
    ratio = value / math.pi
    for denominator in (1, 2, 3, 4, 6, 8, 16):
        numerator = ratio * denominator
        if abs(numerator - round(numerator)) < 1e-9:
            numerator = int(round(numerator))
            sign = "-" if numerator < 0 else ""
            magnitude = abs(numerator)
            head = "π" if magnitude == 1 else f"{magnitude}π"
            return f"{sign}{head}" if denominator == 1 else f"{sign}{head}/{denominator}"
    return f"{value:.3f}"
