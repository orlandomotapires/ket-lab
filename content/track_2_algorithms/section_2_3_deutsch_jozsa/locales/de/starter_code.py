from qiskit import QuantumCircuit

# Qubits 0 bis 2: Eingabe. Qubit 3: Hilfsqubit.
qc = QuantumCircuit(4)

# 1. Hilfsqubit in |−⟩ und Eingabe in Superposition.

oracle(qc)  # die einzige Abfrage an die geheime Funktion

# 2. Interferenz: erneut Hadamard auf die Eingabe.
