from qiskit import QuantumCircuit

# Idea: the Pauli X gate is a half turn about the X axis, so it exchanges the poles of the Bloch sphere.
# One qubit, which starts in |0⟩ at the north pole.
qc = QuantumCircuit(1)
# X|0⟩ = |1⟩: the vector goes from the north pole to the south pole.
qc.x(0)
