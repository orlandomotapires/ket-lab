from fractions import Fraction
from math import gcd

from qiskit import QuantumCircuit

# Qubits 0 bis 3: Zählregister. Qubits 4 bis 7: Arbeitsregister. 4 Bits für die Messung.
qc = QuantumCircuit(8, 4)

# 1. Phasenschätzung der Multiplikation mit 7 modulo 15.
# 2. Inverse QFT auf dem Zählregister und Messung.

# 3. Klassische Nachbearbeitung: von den Zählungen zu den Faktoren.
factors = []
