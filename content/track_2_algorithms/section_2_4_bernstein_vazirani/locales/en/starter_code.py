from qiskit import QuantumCircuit

# Qubits 0 to 3: input. Qubit 4: auxiliary.
qc = QuantumCircuit(5)

# Prepare the input and the auxiliary.

oracle(qc)  # f(x) = s·x mod 2, with secret s

# Interference on the input.
