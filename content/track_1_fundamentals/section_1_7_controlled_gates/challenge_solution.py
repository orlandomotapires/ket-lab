from math import pi
from qiskit import QuantumCircuit

# Idea: find U with U X U† = H, so that conjugating the CNOT target by U turns "apply X" into "apply H".
qc = QuantumCircuit(2)
prepare_input(qc)

# Controlled-H: control qubit 0, target qubit 1.
# R_y(−π/4) X R_y(π/4) = H: a 45° turn about Y takes the X axis onto the axis (X + Z)/√2 of H. The first gate in circuit order is the rightmost factor.
qc.ry(pi / 4, 1)
# The CNOT applies X to the rotated target only when the control is 1.
qc.cx(0, 1)
# R_y(−π/4) completes the sandwich: the target gets H when the control is 1 and the identity when it is 0.
qc.ry(-pi / 4, 1)
