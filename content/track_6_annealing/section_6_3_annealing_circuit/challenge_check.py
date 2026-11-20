"""Challenge of lesson 6.3: a faster anneal than the linear schedule.

Same instance and same gates as the mission. The circuit must reach probability 0.9 of |110>
with at most 300 gates (the mission's linear anneal needs 903 gates for 0.77). The probability
is computed from the state the circuit prepares; no learner variable is read.
"""

import numpy as np
from qiskit import QuantumCircuit

from ket_lab_engine import simulator

THRESHOLD = 0.9
MAX_GATES = 300
ALLOWED = {"h", "rx", "rz", "rzz", "barrier"}
TARGET = 0b110
REVERSED = 0b011


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

    probs = np.abs(simulator.run_trajectory(qc, seed=0).states[-1]) ** 2
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
    return {"passed": False, "key": "not_enough", "params": params, "probability": prob}
