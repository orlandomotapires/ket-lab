from math import pi
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
prepare_input(qc)

# Phase-covariant cloner: |0>|0> -> |00>, |1>|0> -> (|01> + |10>)/sqrt(2).
qc.cry(pi / 2, 0, 1)
qc.cx(1, 0)
