# Idea: each outcome y gives y/16 = s/r, whose reduced denominator divides r.
# The least common multiple of the denominators over several outcomes is r.
from fractions import Fraction
from math import lcm

from qiskit import QuantumCircuit

# N = 15 is provided by the lab; the base a is secret.
qc = QuantumCircuit(8, 4)
# Phase estimation of multiplication by the secret base: counting qubits in |+⟩, work register in |1⟩.
for qubit in range(4):
    qc.h(qubit)
qc.x(4)
for j in range(4):
    apply_controlled_mod_mult(qc, j, 2**j)
inverse_qft(qc, [0, 1, 2, 3])
qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

counts = run_shots(qc)
# Each outcome y gives y/16 = s/r. The denominators (in lowest terms) divide r; their lcm is r.
# One outcome alone can give only a divisor of r (for example s = 0 gives 1), so combine them all.
order = 1
for bits in counts:
    order = lcm(order, Fraction(int(bits, 2), 16).denominator)
