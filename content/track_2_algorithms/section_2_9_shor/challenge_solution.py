from fractions import Fraction
from math import lcm

from qiskit import QuantumCircuit

# N = 15 vem do laboratório; a base a é secreta.
qc = QuantumCircuit(8, 4)
for qubit in range(4):
    qc.h(qubit)
qc.x(4)
for j in range(4):
    apply_controlled_mod_mult(qc, j, 2**j)
inverse_qft(qc, [0, 1, 2, 3])
qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

counts = run_shots(qc)
# Each outcome y gives y/16 = s/r. The denominators (in lowest terms) divide r; their lcm is r.
order = 1
for bits in counts:
    order = lcm(order, Fraction(int(bits, 2), 16).denominator)
