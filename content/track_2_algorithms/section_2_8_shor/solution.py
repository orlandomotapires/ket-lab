from fractions import Fraction
from math import gcd

from qiskit import QuantumCircuit

# a = 7 e N = 15 vêm do laboratório.
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
    r = Fraction(int(bits, 2), 2**4).limit_denominator(N).denominator
    if pow(a, r, N) != 1 or r % 2:  # r precisa ser mesmo um período, e par
        continue
    half = pow(a, r // 2, N)
    if half == N - 1:  # a^(r/2) ≡ -1 (mod N): esta tentativa falha
        continue
    for guess in (gcd(half - 1, N), gcd(half + 1, N)):
        if guess not in (1, N):
            found.add(guess)
factors = sorted(found)
