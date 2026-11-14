from qiskit import QuantumCircuit

# Qubits 0 a 2: entrada. Qubit 3: auxiliar.
qc = QuantumCircuit(4)

# 1. Auxiliar em |−⟩ e entrada em superposição.

oracle(qc)  # a única consulta à função secreta

# 2. Interferência: Hadamard na entrada de novo.
