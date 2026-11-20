"""Validation for lesson 2.10: H = J Z⊗Z + h (X⊗I + I⊗X), J = 1, h = 0.8, t = 2.

The target state is computed here, with the exact matrix exponential, and does not come
from the solution. The learner's circuit may only use rzz and rx (and barriers), at most 90 gates
(30 first-order steps), and the fidelity with e^{-iHt}|00⟩ must be ≥ 0.99.
"""

import numpy as np
from qiskit import QuantumCircuit
from scipy.linalg import expm

from ket_lab_engine import simulator

J, H_FIELD, TIME = 1.0, 0.8, 2.0
TARGET_FIDELITY = 0.99
MAX_GATES = 90
ALLOWED = {"rzz", "rx", "barrier"}

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.diag([1.0, -1.0]).astype(complex)
_I = np.eye(2, dtype=complex)


def exact_state():
    # Qiskit: qubit 0 is the rightmost factor of the tensor product.
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
    if count > MAX_GATES:
        return {"passed": False, "key": "too_many", "params": {"count": count, "limit": MAX_GATES}}
    state = simulator.run_trajectory(qc, seed=0).states[-1]
    fidelity = float(abs(np.vdot(exact_state(), state)) ** 2)
    if fidelity >= TARGET_FIDELITY:
        return {"passed": True, "key": "ok", "params": {"fidelity": fidelity, "count": count}, "fidelity": fidelity}
    return {"passed": False, "key": "low_fidelity", "params": {"fidelity": fidelity, "target": TARGET_FIDELITY}, "fidelity": fidelity}
