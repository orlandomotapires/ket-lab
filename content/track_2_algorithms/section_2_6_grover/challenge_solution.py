# Idea: the success probability after k iterations is sin²((2k + 1)θ), so pick the k that maximizes it.
# For large M the best k can be 0 or small, because more iterations rotate past the target.
from math import asin, pi, sin, sqrt

from qiskit import QuantumCircuit

N = 16
qc = QuantumCircuit(4)

theta = asin(sqrt(num_marked / N))
# Probability after k iterations: sin²((2k + 1)θ). Choose the best k, including k = 0.
# The rounding and the -k break ties in favor of the smaller k, which costs fewer queries.
iterations = max(range(0, 8), key=lambda k: (round(sin((2 * k + 1) * theta) ** 2, 9), -k))


def diffuser(qc):
    # Inversion about the mean: H·X, a Z controlled by all qubits, then X·H.
    for qubit in range(4):
        qc.h(qubit)
        qc.x(qubit)
    qc.h(3)
    qc.mcx([0, 1, 2], 3)
    qc.h(3)
    for qubit in range(4):
        qc.x(qubit)
        qc.h(qubit)


# Uniform superposition on the four qubits.
for qubit in range(4):
    qc.h(qubit)

# Oracle and diffuser, repeated the number of times chosen above.
for _ in range(iterations):
    oracle(qc)
    diffuser(qc)
