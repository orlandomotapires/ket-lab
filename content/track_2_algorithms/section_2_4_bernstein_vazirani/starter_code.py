from qiskit import QuantumCircuit

# Qubits 0 to 3: input. Qubit 4: auxiliary.
qc = QuantumCircuit(5)

# Prepare the auxiliary qubit in |−⟩ and the input in uniform superposition.

oracle(qc)  # f(x) = s·x mod 2, with s hidden

# Hadamard on every input qubit, so the amplitudes interfere.
