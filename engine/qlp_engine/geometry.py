"""Tradução do vetor de estado em grandezas prontas para renderização."""

from __future__ import annotations

import math

import numpy as np

from .simulator import Op, StepRecord, Trajectory

DECIMALS = 6


def reduced_density(state: np.ndarray, n: int, qubit: int) -> np.ndarray:
    """Matriz densidade 2x2 de um qubit, a partir de um vetor de estado ou de uma matriz densidade."""
    if state.ndim == 2:
        tensor = state.reshape((2,) * (2 * n))
        row, col = n - 1 - qubit, 2 * n - 1 - qubit
        moved = np.moveaxis(tensor, (row, col), (0, n))
        return np.einsum("ajbj->ab", moved.reshape(2, 2 ** (n - 1), 2, 2 ** (n - 1)))
    m = np.moveaxis(state.reshape((2,) * n), n - 1 - qubit, 0).reshape(2, -1)
    return m @ m.conj().T


def bloch_vectors(state: np.ndarray, n: int) -> tuple[list[list[float]], list[float]]:
    """Vetor de Bloch (x, y, z) e pureza Tr(rho^2) do estado reduzido de cada qubit.

    Um qubit emaranhado, ou sujeito a ruído, tem estado local misto: o vetor encolhe (|r| < 1).
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


def snapshot(state: np.ndarray, n: int) -> dict:
    """Estado pronto para a interface. Estados mistos não têm amplitudes (`None`)."""
    vectors, purities = bloch_vectors(state, n)
    if state.ndim == 2:
        probabilities = np.clip(np.real(np.diag(state)), 0.0, None)
        amplitudes = None
        total_purity = float(np.real(np.trace(state @ state)))
    else:
        probabilities = np.abs(state) ** 2
        rounded = np.round(state, DECIMALS)
        amplitudes = [[float(a.real), float(a.imag)] for a in rounded]
        total_purity = 1.0
    return {
        "amplitudes": amplitudes,
        "probabilities": [round(float(p), DECIMALS) for p in probabilities],
        "bloch": vectors,
        "purity": purities,
        "state_purity": round(total_purity, DECIMALS),
    }


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


def describe_trajectory(trajectory: Trajectory) -> dict:
    n = trajectory.num_qubits
    return {
        "num_qubits": n,
        "num_clbits": trajectory.num_clbits,
        "steps": [describe_step(i, record) for i, record in enumerate(trajectory.steps)],
        "snapshots": [snapshot(state, n) for state in trajectory.states],
        "clbits": trajectory.clbits,
        "has_measurement": any(r.outcome is not None for r in trajectory.steps),
    }


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
    "bitflip": "BitFlip",
    "phaseflip": "PhaseFlip",
    "depolarizing": "Dep",
    "amplitudedamping": "AmpDamp",
    "phasedamping": "PhaseDamp",
}


def _label(op: Op) -> str:
    name = op.base if op.num_ctrl and op.base and op.name not in _NAMES else op.name
    # Nomes que não são identificadores ("U^4", "×7^2") são mostrados como estão.
    base = _NAMES.get(name) or (name.upper() if name.isidentifier() else name)
    if op.kind == "conditional" and op.condition is not None:
        bits, value = op.condition
        inner = " ".join(_label(child) for child in op.body) or "…"
        target = f"c{bits[0]}" if len(bits) == 1 else "c"
        return f"{inner} se {target}={value}"
    if op.params:
        return f"{base}({', '.join(format_angle(p) for p in op.params)})"
    return base


def format_angle(value: float) -> str:
    """Escreve ângulos como frações de π quando possível (ex.: π/2, 3π/4)."""
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
