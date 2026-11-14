from fractions import Fraction
from math import gcd

from qiskit import QuantumCircuit

qc = QuantumCircuit(8, 4)
for qubit in range(4):
    qc.h(qubit)
qc.x(4)
for j in range(4):
    apply_controlled_mod_mult(qc, j, 2**j)
inverse_qft(qc, [0, 1, 2, 3])
qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

counts = run_shots(qc)
found = set()
for bits in counts:
    r = Fraction(int(bits, 2) / 16).limit_denominator(15).denominator
    if r % 2 == 0:
        for guess in (gcd(7 ** (r // 2) - 1, 15), gcd(7 ** (r // 2) + 1, 15)):
            if guess not in (1, 15):
                found.add(guess)
factors = sorted(found)
