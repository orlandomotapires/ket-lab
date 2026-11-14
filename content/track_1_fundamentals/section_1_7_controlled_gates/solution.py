from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
prepare_input(qc)

# CS = diag(1, 1, 1, i): fase de 90° só quando os dois qubits valem 1.
qc.t(0)
qc.t(1)
qc.cx(0, 1)  # o qubit 1 passa a guardar a paridade a ⊕ b
qc.tdg(1)
qc.cx(0, 1)
