from math import pi
from qiskit import QuantumCircuit

# Idea: qubit 0 gets a biased rotation, qubit 1 a fair coin, and qubit 2 is steered to |1⟩ through |−⟩ using only H and Z.
qc = QuantumCircuit(3, 3)
# R_y(π/3) gives sin²(π/6) = 1/4, the probability of reading 1 on qubit 0.
qc.ry(pi / 3, 0)
# Hadamard on qubit 1: |+⟩ gives 0 and 1 with probability 1/2 each.
qc.h(1)
# H then Z builds |−⟩ on qubit 2 (Z flips the sign of the |1⟩ amplitude of |+⟩).
qc.h(2)
qc.z(2)
# H·H = I and |−⟩ = H|1⟩, so this Hadamard maps |−⟩ to |1⟩ and bit 2 is always 1.
qc.h(2)
# Measure each qubit into the classical bit with the same index.
for q in range(3):
    qc.measure(q, q)
