from qiskit import QuantumCircuit

# Qubit 0: Kontrolle. Qubit 1: Ziel.
qc = QuantumCircuit(2)

# 1. Ziel in |−⟩ und Kontrolle in |+⟩.
# 2. CNOT von der Kontrolle (0) auf das Ziel (1).
