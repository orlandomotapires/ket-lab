from qiskit import QuantumCircuit

# Qubit 0: entrada. Qubit 1: auxiliar.
qc = QuantumCircuit(2)

# 1. Auxiliar em |−⟩ e entrada em |+⟩.

oracle(qc)  # a única consulta à função secreta

# 2. Interferência: Hadamard na entrada de novo.
