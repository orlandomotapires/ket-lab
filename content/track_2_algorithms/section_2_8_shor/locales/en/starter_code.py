from fractions import Fraction
from math import gcd

from qiskit import QuantumCircuit

# a = 7 and N = 15 are provided by the lab.
# Qubits 0 to 3: counting. Qubits 4 to 7: work. 4 bits for the measurement.
qc = QuantumCircuit(8, 4)

# 1. Phase estimation of multiplication by 7 modulo 15.
# 2. Inverse QFT on the counting qubits and measurement.

# 3. Classical post-processing: from the counts to the factors.
factors = []
