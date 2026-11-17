# Idea: phase estimation of multiplication by 7 gives m/16 ≈ s/r. Continued fractions recover r,
# and for an even r with 7^(r/2) ≢ −1 the gcds of 7^(r/2) ± 1 with 15 are the factors.
from fractions import Fraction
from math import gcd

from qiskit import QuantumCircuit

# a = 7 and N = 15 are provided by the lab.
qc = QuantumCircuit(8, 4)
# Counting qubits in |+⟩, so that each controlled multiplication kicks a phase back onto its qubit.
for qubit in range(4):
    qc.h(qubit)
# Work register in |1⟩, a superposition of the eigenvectors of multiplication by 7.
qc.x(4)
# Counting qubit j controls multiplication by 7^(2^j) mod 15, which is U^(2^j).
for j in range(4):
    apply_controlled_mod_mult(qc, j, 2**j)
# The inverse QFT turns the phases s/r on the counting register into the integer m ≈ 16·s/r.
inverse_qft(qc, [0, 1, 2, 3])
qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

counts = run_shots(qc)
found = set()
for bits in counts:
    # Continued fractions: the closest fraction to m/16 with denominator at most N gives r.
    r = Fraction(int(bits, 2), 2**4).limit_denominator(N).denominator
    if pow(a, r, N) != 1 or r % 2:  # r must really be a period, and even
        continue
    half = pow(a, r // 2, N)
    if half == N - 1:  # a^(r/2) ≡ -1 (mod N): this attempt fails
        continue
    # (half − 1)(half + 1) is a multiple of N, so each gcd with N can be a nontrivial factor.
    for guess in (gcd(half - 1, N), gcd(half + 1, N)):
        if guess not in (1, N):
            found.add(guess)
factors = sorted(found)
