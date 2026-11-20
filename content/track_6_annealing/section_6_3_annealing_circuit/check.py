"""Validation for lesson 6.3: quantum annealing as a circuit on three qubits.

The instance (h, J) is the three-qubit number-partitioning problem of lessons 6.1 and 6.2; its
ground state is s = (+1, -1, -1), the basis state |110> (Qiskit label, qubit 0 on the right).
The learner's circuit may use h, rx, rz and rzz only, at most 1000 gates. The probability of
|110> is read from the state the circuit prepares, never from a variable, and must be at least 0.7.
"""

import numpy as np
from qiskit import QuantumCircuit

from ket_lab_engine import simulator

THRESHOLD = 0.7
MAX_GATES = 1000
ALLOWED = {"h", "rx", "rz", "rzz", "barrier"}
TARGET = 0b110  # q2 = 1, q1 = 1, q0 = 0
REVERSED = 0b011  # the same pattern with the qubit order reversed


def check(ns, run_case):
    qc = ns.get("qc")
    if not isinstance(qc, QuantumCircuit):
        return {"passed": False, "key": "no_circuit"}
    if qc.num_qubits != 3:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": qc.num_qubits}}
    names = {i.operation.name for i in qc.data}
    if names - ALLOWED:
        return {"passed": False, "key": "gates", "params": {"names": ", ".join(sorted(names - ALLOWED))}}
    count = sum(1 for i in qc.data if i.operation.name != "barrier")
    if count > MAX_GATES:
        return {"passed": False, "key": "too_many", "params": {"count": count, "limit": MAX_GATES}}
    hadamard_qubits = {qc.find_bit(q).index for i in qc.data if i.operation.name == "h" for q in i.qubits}
    if hadamard_qubits != {0, 1, 2}:
        return {"passed": False, "key": "no_hadamard"}
    if not ({"rx"} <= names and names & {"rz", "rzz"}):
        return {"passed": False, "key": "no_layers"}

    state = simulator.run_trajectory(qc, seed=0).states[-1]
    probs = np.abs(state) ** 2
    prob = float(probs[TARGET])
    params = {"prob": prob, "target": THRESHOLD, "count": count}
    if prob >= THRESHOLD:
        return {"passed": True, "key": "ok", "params": params, "probability": prob}
    if probs[REVERSED] >= 0.3 and probs[REVERSED] > prob:
        params["other"] = float(probs[REVERSED])
        return {"passed": False, "key": "reversed", "params": params, "probability": prob}
    if probs[0] >= 0.5:
        params["other"] = float(probs[0])
        return {"passed": False, "key": "sign", "params": params, "probability": prob}
    return {"passed": False, "key": "not_converged", "params": params, "probability": prob}
