from qiskit import QuantumCircuit

# Qubit 0: input. Qubit 1: auxiliary.
qc = QuantumCircuit(2)

# 1. Auxiliary in |−⟩ and input in |+⟩.

oracle(qc)  # the single query to the secret function

# 2. Interference: Hadamard on the input again.
