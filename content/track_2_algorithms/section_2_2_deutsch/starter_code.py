from qiskit import QuantumCircuit

# Qubit 0: input. Qubit 1: auxiliary.
qc = QuantumCircuit(2)

# 1. Prepare the auxiliary qubit in |−⟩ and the input in |+⟩.

oracle(qc)  # the single query to the hidden function

# 2. Hadamard on the input, so the two amplitudes interfere.
