from qiskit import QuantumCircuit

# Qubit 0: Eingabe. Qubit 1: Hilfsqubit.
qc = QuantumCircuit(2)

# 1. Hilfsqubit in |−⟩ und Eingabe in |+⟩.

oracle(qc)  # die einzige Abfrage an die geheime Funktion

# 2. Interferenz: erneut Hadamard auf die Eingabe.
