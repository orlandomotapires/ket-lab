from math import asin, pi, sin, sqrt

from qiskit import QuantumCircuit

N = 16
qc = QuantumCircuit(4)

theta = asin(sqrt(num_marked / N))
# Probability after k iterations: sin²((2k + 1)θ). Choose the best k, including k = 0.
iterations = max(range(0, 8), key=lambda k: (round(sin((2 * k + 1) * theta) ** 2, 9), -k))


def diffuser(qc):
    for qubit in range(4):
        qc.h(qubit)
        qc.x(qubit)
    qc.h(3)
    qc.mcx([0, 1, 2], 3)
    qc.h(3)
    for qubit in range(4):
        qc.x(qubit)
        qc.h(qubit)


for qubit in range(4):
    qc.h(qubit)

for _ in range(iterations):
    oracle(qc)
    diffuser(qc)
