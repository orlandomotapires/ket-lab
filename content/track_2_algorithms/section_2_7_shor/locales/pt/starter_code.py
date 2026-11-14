from fractions import Fraction
from math import gcd

from qiskit import QuantumCircuit

# Qubits 0 a 3: contagem. Qubits 4 a 7: trabalho. 4 bits para a medição.
qc = QuantumCircuit(8, 4)

# 1. Estimação de fase da multiplicação por 7 módulo 15.
# 2. QFT inversa na contagem e medição.

# 3. Pós-processamento clássico: das contagens aos fatores.
factors = []
