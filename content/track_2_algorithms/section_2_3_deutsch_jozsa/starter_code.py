from qiskit import QuantumCircuit

# Qubits 0 to 2: input. Qubit 3: auxiliary.
qc = QuantumCircuit(4)

# 1. Prepare the auxiliary qubit in |−⟩ and the input in uniform superposition.

oracle(qc)  # the single query to the hidden function

# 2. Hadamard on every input qubit, so the amplitudes interfere.
