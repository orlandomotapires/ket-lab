from math import pi
from qiskit import QuantumCircuit

qc = QuantumCircuit(3, 3)
qc.ry(pi / 3, 0)
qc.h(1)
qc.h(2)
for q in range(3):
    qc.measure(q, q)
