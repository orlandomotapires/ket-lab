"""Validation for lesson 4.2: the logical state α|000⟩ + β|111⟩ survives any single
bit flip, for several input states; and bit-flip noise on all the
qubits follows the formula 1 − 3p² + 2p³.

The fidelity is computed from the gates and channels of the learner's circuit.
"""

import numpy as np

from qlp_engine import pl, simulator

INPUTS = [(0.0, 0.0), (np.pi / 2, 0.0), (1.1, 0.7)]
SINGLE_ERRORS = ["none", "x0", "x1", "x2"]
P = 0.1
EXPECTED_NOISY = 1 - 3 * P**2 + 2 * P**3  # 0.972
TOLERANCE = 0.999


def logical_state(theta, phi):
    """α|000⟩ + β|111⟩ for |ψ⟩ = RZ(φ) RY(θ) |0⟩ (the global phase does not matter)."""
    alpha = np.cos(theta / 2) * np.exp(-1j * phi / 2)
    beta = np.sin(theta / 2) * np.exp(1j * phi / 2)
    psi = np.zeros(8, dtype=complex)
    psi[0], psi[7] = alpha, beta
    return psi


def data_density(state, n):
    """Density matrix of qubits 0, 1 and 2 (discards the ancillas)."""
    rho = state if state.ndim == 2 else np.outer(state, state.conj())
    keep = 3
    tensor = rho.reshape((2,) * (2 * n))
    # row index: qubits n-1 ... 0 (qubit 0 is axis n-1); the ancillas are the high qubits.
    traced = np.einsum("abxyzabuvw->xyzuvw", tensor)  # sum over q4 and q3 (row = column)
    return traced.reshape(2**keep, 2**keep)


def fidelity(run_case, theta, phi, error, p=P):
    ns = run_case({"input": [theta, phi], "error": error, "p": p})
    circuit = ns.get("circuit")
    ops, lines, n = pl.trace_qnode(circuit, [])
    if n != 5:
        raise ValueError(n)
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    psi = logical_state(theta, phi)
    return float(np.real(psi.conj() @ data_density(state, n) @ psi))


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    _, _, n = pl.trace_qnode(circuit, [])
    if n != 5:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    for theta, phi in INPUTS:
        for error in SINGLE_ERRORS:
            f = fidelity(run_case, theta, phi, error)
            if f < TOLERANCE:
                key = "encode_wrong" if error == "none" else "single_fail"
                return {"passed": False, "key": key, "params": {"error": error.upper(), "fidelity": f}}
    # With |0⟩, a logical error gives an orthogonal state: the fidelity is the success
    # probability, 1 − 3p² + 2p³. For a generic state, a logical X still overlaps with |ψ⟩.
    noisy = fidelity(run_case, 0.0, 0.0, "bitflip")
    if abs(noisy - EXPECTED_NOISY) > 0.003:
        return {"passed": False, "key": "noisy_mismatch", "params": {"fidelity": noisy, "expected": EXPECTED_NOISY}}
    return {"passed": True, "key": "ok", "params": {"fidelity": noisy, "bare": 1 - P}}
