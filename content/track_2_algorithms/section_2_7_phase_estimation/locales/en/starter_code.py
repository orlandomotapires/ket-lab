from qiskit import QuantumCircuit

# Qubits 0 to 2: counting. Qubit 3: eigenvector of U. 3 bits for the measurement.
qc = QuantumCircuit(4, 3)

# 1. Prepare the eigenvector and the superposition on the counting qubits.
# 2. Controlled powers: apply_controlled_u(qc, control, power).
# 3. inverse_qft(qc, [0, 1, 2]) and measurement of the counting qubits.

# 4. Read the result and estimate the phase.
theta = None
