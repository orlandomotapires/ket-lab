from qiskit import QuantumCircuit

# Qubits 0 bis 3: Eingabe. Qubit 4: Hilfsqubit.
qc = QuantumCircuit(5)

# Bereite die Eingabe und das Hilfsqubit vor.

oracle(qc)  # f(x) = s·x mod 2, mit geheimem s

# Interferenz auf der Eingabe.
