"""Validação da lição 3.6: o estado lógico α|000⟩ + β|111⟩ sobrevive a qualquer
bit flip único, para vários estados de entrada; e o ruído de bit flip em todos os
qubits segue a fórmula 1 − 3p² + 2p³.

A fidelidade é calculada a partir das portas e canais do circuito do aluno.
"""

import numpy as np

from qlp_engine import pl, simulator

INPUTS = [(0.0, 0.0), (np.pi / 2, 0.0), (1.1, 0.7)]
SINGLE_ERRORS = ["none", "x0", "x1", "x2"]
P = 0.1
EXPECTED_NOISY = 1 - 3 * P**2 + 2 * P**3  # 0,972
TOLERANCE = 0.999


def logical_state(theta, phi):
    """α|000⟩ + β|111⟩ para |ψ⟩ = RZ(φ) RY(θ) |0⟩ (a fase global não importa)."""
    alpha = np.cos(theta / 2) * np.exp(-1j * phi / 2)
    beta = np.sin(theta / 2) * np.exp(1j * phi / 2)
    psi = np.zeros(8, dtype=complex)
    psi[0], psi[7] = alpha, beta
    return psi


def data_density(state, n):
    """Matriz densidade dos qubits 0, 1 e 2 (descarta as ancillas)."""
    rho = state if state.ndim == 2 else np.outer(state, state.conj())
    keep = 3
    tensor = rho.reshape((2,) * (2 * n))
    # índice de linha: qubits n-1 … 0 (o qubit 0 é o eixo n-1); as ancillas são os qubits altos.
    traced = np.einsum("abxyzabuvw->xyzuvw", tensor)  # soma sobre q4 e q3 (linha = coluna)
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
    # Com |0⟩, um erro lógico dá um estado ortogonal: a fidelidade é a probabilidade de
    # sucesso, 1 − 3p² + 2p³. Num estado genérico, um X lógico ainda tem sobreposição com |ψ⟩.
    noisy = fidelity(run_case, 0.0, 0.0, "bitflip")
    if abs(noisy - EXPECTED_NOISY) > 0.003:
        return {"passed": False, "key": "noisy_mismatch", "params": {"fidelity": noisy, "expected": EXPECTED_NOISY}}
    return {"passed": True, "key": "ok", "params": {"fidelity": noisy, "bare": 1 - P}}
