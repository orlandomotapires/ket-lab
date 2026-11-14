from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
prepare_input(qc)  # uma entrada de dois qubits, você não sabe qual

# Sua missão: construa a porta S controlada (CS = diag(1, 1, 1, i)) com
# apenas cx, t e tdg. A fase de 90° deve aparecer só quando os dois qubits valem 1.
