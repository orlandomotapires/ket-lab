from qiskit import QuantumCircuit

# Qubits 0 a 3: entrada. Qubit 4: auxiliar.
qc = QuantumCircuit(5)

# Prepare a entrada e o auxiliar.

oracle(qc)  # f(x) = s·x mod 2, com s secreta

# Interferência na entrada.
