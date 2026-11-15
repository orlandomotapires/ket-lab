from math import pi
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
prepare_input(qc)

# Controlled-H: control qubit 0, target qubit 1.
qc.ry(pi / 4, 1)
qc.cx(0, 1)
qc.ry(-pi / 4, 1)
