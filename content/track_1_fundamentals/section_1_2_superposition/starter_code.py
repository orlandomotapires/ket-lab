from qiskit import QuantumCircuit

# 3 qubits and 3 classical bits for the measurement results.
qc = QuantumCircuit(3, 3)

# Mission: put all three qubits in an equal superposition, then measure each qubit into the classical bit with the same index.
