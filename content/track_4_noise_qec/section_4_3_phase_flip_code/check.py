"""Validation for lesson 4.3: the logical state α|+++⟩ + β|−−−⟩ survives any single
phase flip (and the no-error case), for several input states.

The fidelity is computed from the gates of the learner's circuit.
"""

import numpy as np

from qlp_engine import pl, simulator

INPUTS = [(0.0, 0.0), (np.pi / 2, 0.0), (1.1, 0.7), (2.4, -1.3)]
SINGLE_ERRORS = ["none", "z0", "z1", "z2"]
TOLERANCE = 0.999


def logical_state(theta, phi):
    """α|+++⟩ + β|−−−⟩ for |ψ⟩ = RZ(φ) RY(θ) |0⟩ (the global phase does not matter)."""
    alpha = np.cos(theta / 2) * np.exp(-1j * phi / 2)
    beta = np.sin(theta / 2) * np.exp(1j * phi / 2)
    plus = np.ones(2) / np.sqrt(2)
    minus = np.array([1, -1]) / np.sqrt(2)
    return alpha * np.kron(np.kron(plus, plus), plus) + beta * np.kron(np.kron(minus, minus), minus)


def data_density(state, n):
    """Density matrix of qubits 0, 1 and 2 (discards the ancillas, which are qubits 3 and 4)."""
    rho = state if state.ndim == 2 else np.outer(state, state.conj())
    tensor = rho.reshape((2,) * (2 * n))
    traced = np.einsum("abxyzabuvw->xyzuvw", tensor)
    return traced.reshape(8, 8)


def fidelity(run_case, theta, phi, error):
    ns = run_case({"input": [theta, phi], "error": error})
    ops, lines, n = pl.trace_qnode(ns.get("circuit"), [])
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
    return {"passed": True, "key": "ok"}
