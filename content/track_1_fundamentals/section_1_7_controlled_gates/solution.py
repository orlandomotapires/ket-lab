from qiskit import QuantumCircuit

# Idea: the phase π/2·ab of CS is a sum of T phases on a, b and (a ⊕ b), because a + b − (a ⊕ b) = 2ab.
qc = QuantumCircuit(2)
prepare_input(qc)

# CS = diag(1, 1, 1, i): a 90° phase only when both qubits are 1.
# Each T adds π/4 for every qubit that is 1: π/4·(a + b) so far.
qc.t(0)
qc.t(1)
# Qubit 1 now holds the parity a ⊕ b (the CNOT writes it there).
qc.cx(0, 1)
# T† on the parity subtracts π/4·(a ⊕ b), leaving π/4·2ab = π/2·ab.
qc.tdg(1)
# Undo the CNOT so that qubit 1 holds b again and the amplitudes keep their labels.
qc.cx(0, 1)
