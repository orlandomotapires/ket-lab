"""Challenge for lesson 2.10: same Hamiltonian and target state as the mission (exact matrix
exponential), but with at most 20 gates and fidelity ≥ 0.995. Only the second-order
(symmetric) formula with the half steps of the field merged gets there: 5 steps, 17 gates."""

import numpy as np
from qiskit import QuantumCircuit
from scipy.linalg import expm

from ket_lab_engine import simulator

J, H_FIELD, TIME = 1.0, 0.8, 2.0
TARGET_FIDELITY = 0.995
MAX_GATES = 20
ALLOWED = {"rzz", "rx", "barrier"}

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.diag([1.0, -1.0]).astype(complex)
_I = np.eye(2, dtype=complex)


def exact_state():
    hamiltonian = J * np.kron(_Z, _Z) + H_FIELD * (np.kron(_I, _X) + np.kron(_X, _I))
    return expm(-1j * hamiltonian * TIME)[:, 0]


def check(ns, run_case):
    qc = ns.get("qc")
    if not isinstance(qc, QuantumCircuit):
        return {"passed": False, "key": "no_circuit"}
    if qc.num_qubits != 2:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": qc.num_qubits}}
    names = {i.operation.name for i in qc.data}
    if names - ALLOWED:
        return {"passed": False, "key": "gates", "params": {"names": ", ".join(sorted(names - ALLOWED))}}
    count = sum(1 for i in qc.data if i.operation.name != "barrier")
    state = simulator.run_trajectory(qc, seed=0).states[-1]
    fidelity = float(abs(np.vdot(exact_state(), state)) ** 2)
    if count > MAX_GATES:
        return {"passed": False, "key": "too_many", "params": {"count": count, "limit": MAX_GATES}, "fidelity": fidelity}
    if fidelity >= TARGET_FIDELITY:
        return {"passed": True, "key": "ok", "params": {"fidelity": fidelity, "count": count}, "fidelity": fidelity}
    return {"passed": False, "key": "low_fidelity", "params": {"fidelity": fidelity, "target": TARGET_FIDELITY}, "fidelity": fidelity}
