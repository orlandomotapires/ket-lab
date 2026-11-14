from qiskit import QuantumCircuit

# Qubits 0 bis 2: Zählregister. Qubit 3: Eigenvektor von U. 3 Bits für die Messung.
qc = QuantumCircuit(4, 3)

# 1. Bereite den Eigenvektor und die Superposition im Zählregister vor.
# 2. Kontrollierte Potenzen: apply_controlled_u(qc, kontrolle, potenz).
# 3. inverse_qft(qc, [0, 1, 2]) und Messung des Zählregisters.

# 4. Lies das Ergebnis aus und schätze die Phase.
theta = None
