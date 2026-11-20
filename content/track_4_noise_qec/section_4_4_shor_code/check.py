"""Validation for lesson 4.4: the logical state of the Shor code survives any
X, Y or Z error on each of the nine qubits (and the no-error case), and also an
arbitrary rotation on each qubit (error discretization).

The criterion is the fidelity of qubit 0 with |ψ⟩ after decoding.
"""

import numpy as np

from ket_lab_engine import pl, simulator

INPUTS = [(0.0, 0.0), (np.pi / 2, 0.0), (1.1, 0.7), (2.4, -1.3)]
ERRORS = ["none"] + [f"{kind}{q}" for kind in "xyzu" for q in range(9)]
TOLERANCE = 0.999


def qubit0_state(state, n):
    """Density matrix of qubit 0 (qubit 0 is the least significant axis of the vector)."""
    if state.ndim == 2:
        tensor = state.reshape((2,) * (2 * n))
        axes = "abcdefghi"[: n - 1]
        return np.einsum(f"{axes}x{axes}y->xy", tensor)
    matrix = state.reshape(-1, 2)
    return matrix.T @ matrix.conj()


def input_state(theta, phi):
    return np.array([np.cos(theta / 2) * np.exp(-1j * phi / 2), np.sin(theta / 2) * np.exp(1j * phi / 2)])


def fidelity(run_case, theta, phi, error):
    ns = run_case({"input": [theta, phi], "error": error})
    ops, lines, n = pl.trace_qnode(ns.get("circuit"), [])
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    psi = input_state(theta, phi)
    rho = qubit0_state(state, n)
    return float(np.real(psi.conj() @ rho @ psi))


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    _, _, n = pl.trace_qnode(circuit, [])
    if n != 9:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    for theta, phi in INPUTS:
        for error in ERRORS:
            f = fidelity(run_case, theta, phi, error)
            if f < TOLERANCE:
                key = "encode_wrong" if error == "none" else "single_fail"
                return {"passed": False, "key": key, "params": {"error": error.upper(), "fidelity": f}}
    return {"passed": True, "key": "ok"}
