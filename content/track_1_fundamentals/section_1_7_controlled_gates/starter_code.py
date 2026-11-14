from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
prepare_input(qc)  # unknown two-qubit input

# Mission: build the controlled-S gate (CS = diag(1, 1, 1, i)) using
# only cx, t and tdg. The 90° phase applies only when both qubits are 1.
