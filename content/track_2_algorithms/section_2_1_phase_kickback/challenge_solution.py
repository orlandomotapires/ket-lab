from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.x(1)
qc.h(0)
qc.cp(pi / 2, 0, 1)
