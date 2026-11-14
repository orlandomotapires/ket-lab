from qiskit import QuantumCircuit

# 3 qubits and 3 classical bits (to store the measurement results).
qc = QuantumCircuit(3, 3)

# Your mission: uniform superposition on all three qubits, then measure each qubit into the bit with the same index.
