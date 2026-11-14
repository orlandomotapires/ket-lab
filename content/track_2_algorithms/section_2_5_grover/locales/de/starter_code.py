from qiskit import QuantumCircuit

N = 16
qc = QuantumCircuit(4)

# num_marked (M) stellt das Labor bereit: wie viele Elemente das Orakel markiert.
iterations = 0  # aus N und num_marked berechnen


def diffuser(qc):
    # Spiegelung am Mittelwert: H, X, mehrfach kontrolliertes Z, X, H.
    pass


# 1. Gleichmäßige Superposition auf den 4 Qubits.
# 2. Grover-Iterationen: oracle(qc) gefolgt von diffuser(qc).
