from math import pi
from qiskit import QuantumCircuit

# Idea: undo the sequence by applying the inverse of each gate in reverse order; (U3 U2 U1)⁻¹ = U1† U2† U3†.
qc = QuantumCircuit(1)
prepare_input(qc)

qc.x(0)
qc.h(0)
qc.s(0)
qc.t(0)
qc.h(0)
qc.p(pi / 3, 0)

# The last gate applied is the first one undone. R_z(−π/3) = e^{iπ/6} P(−π/3), so it inverts P(π/3) up to a global phase.
qc.rz(-pi / 3, 0)
# H is its own inverse, so the same gate undoes the last H.
qc.h(0)
# T† is a −45° rotation about Z and cancels the T gate.
qc.tdg(0)
# S† is a −90° rotation about Z and cancels the S gate.
qc.sdg(0)
# The first H of the sequence is undone by H again.
qc.h(0)
# X is its own inverse and was applied first, so it is undone last.
qc.x(0)
