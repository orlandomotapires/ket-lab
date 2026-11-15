"""Desafio da lição 1.8: clonador covariante em fase.

Para entradas no equador da esfera de Bloch, a fidelidade de cada uma das duas
saídas (estado reduzido de cada qubit) com a entrada precisa chegar a 0,85.
O valor ótimo é (1 + 1/√2)/2 ≈ 0,8536; um CNOT dá 0,5.
"""

from math import pi

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace

PHASES = [0.0, pi / 2, pi, 3 * pi / 2, 0.7]
THRESHOLD = 0.85


def check(ns, run_case):
    worst = 1.0
    for phi in PHASES:
        circuit = run_case((pi / 2, phi)).get("qc")
        if not isinstance(circuit, QuantumCircuit) or circuit.num_qubits != 2:
            return {"passed": False, "key": "wrong_size"}
        if any(i.operation.name in ("measure", "reset") for i in circuit.data):
            return {"passed": False, "key": "no_measure"}
        state = Statevector(circuit)
        target = np.array([1, np.exp(1j * phi)]) / np.sqrt(2)
        for qubit in (0, 1):
            rho = partial_trace(state, [1 - qubit]).data
            worst = min(worst, float(np.real(target.conj() @ rho @ target)))
    if worst < THRESHOLD:
        return {"passed": False, "key": "low", "params": {"fidelity": worst, "threshold": THRESHOLD}}
    return {"passed": True, "key": "ok", "params": {"fidelity": worst}}
