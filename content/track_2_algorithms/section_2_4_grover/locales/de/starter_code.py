from qiskit import QuantumCircuit

qc = QuantumCircuit(4)


def diffuser(qc):
    # Spiegelung am Mittelwert: H, X, mehrfach kontrolliertes Z, X, H.
    pass


# 1. Gleichmäßige Superposition auf den 4 Qubits.
# 2. Grover-Iterationen: oracle(qc) gefolgt von diffuser(qc).
