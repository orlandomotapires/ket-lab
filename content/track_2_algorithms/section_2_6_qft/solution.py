from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
prepare_input(qc)

qc.h(2)
qc.cp(pi / 2, 1, 2)
qc.cp(pi / 4, 0, 2)
qc.h(1)
qc.cp(pi / 2, 0, 1)
qc.h(0)
qc.swap(0, 2)
