from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
prepare_input(qc)  # a two-qubit input, you do not know which

# Your mission: build the controlled-S gate (CS = diag(1, 1, 1, i)) using
# only cx, t and tdg. The 90° phase must appear only when both qubits are 1.
