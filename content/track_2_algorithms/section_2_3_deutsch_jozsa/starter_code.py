from qiskit import QuantumCircuit

# Qubits 0 to 2: input. Qubit 3: auxiliary.
qc = QuantumCircuit(4)

# 1. Auxiliary in |−⟩ and input in superposition.

oracle(qc)  # the single query to the secret function

# 2. Interference: Hadamard on the input again.
