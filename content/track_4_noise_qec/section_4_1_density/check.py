"""Validation for lesson 4.1: the density matrix of the circuit with error, for several
error probabilities, and the values derived from it (wrong answer and purity).

The state is rebuilt from the gates and channels of the learner's circuit, without
trusting what the QNode returns.
"""

import numpy as np

from ket_lab_engine import pl, simulator

CASES = [(0.2, 0.2), (0.1, 0.3), (0.3, 0.05)]
I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
T = np.diag([1, np.exp(1j * np.pi / 4)])


def reference(p_x, p_z):
    psi = T @ H @ np.array([1, 0], dtype=complex)
    rho = np.outer(psi, psi.conj())
    rho = (1 - p_x - p_z) * rho + p_x * X @ rho @ X + p_z * Z @ rho @ Z
    after = H @ T.conj().T
    return after @ rho @ after.conj().T


def student_rho(circuit, p_x, p_z):
    ops, lines, n = pl.trace_qnode(circuit, [p_x, p_z])
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    if state.ndim == 1:
        state = np.outer(state, state.conj())
    return state, n


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    for p_x, p_z in CASES:
        rho, n = student_rho(circuit, p_x, p_z)
        if n != 1:
            return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
        expected = reference(p_x, p_z)
        distance = 0.5 * np.sum(np.abs(np.linalg.eigvalsh(rho - expected)))
        if distance > 1e-6:
            got, want = float(np.real(rho[1, 1])), float(np.real(expected[1, 1]))
            key = "no_noise" if abs(np.real(np.trace(rho @ rho)) - 1) < 1e-9 else "wrong_rho"
            return {"passed": False, "key": key, "params": {"px": p_x, "pz": p_z, "got": got, "want": want}}
    expected = reference(0.2, 0.2)
    p_wrong = float(np.real(expected[1, 1]))
    purity = float(np.real(np.trace(expected @ expected)))
    for name, value in (("p_wrong", p_wrong), ("purity", purity)):
        if name not in ns:
            return {"passed": False, "key": "missing", "params": {"name": name}}
        try:
            actual = float(np.real(ns[name]))
        except (TypeError, ValueError):
            return {"passed": False, "key": "missing", "params": {"name": name}}
        if abs(actual - value) > 1e-6:
            return {"passed": False, "key": "wrong_value", "params": {"name": name, "actual": actual}}
    return {"passed": True, "key": "ok", "params": {"p_wrong": p_wrong, "purity": purity}}
