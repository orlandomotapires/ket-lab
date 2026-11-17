# Idea: start in the uniform superposition and repeat oracle + diffuser floor(π/4·√(N/M)) times,
# each repetition rotating the state by 2θ toward the marked items.
from math import floor, pi, sqrt

from qiskit import QuantumCircuit

N = 16
qc = QuantumCircuit(4)

# num_marked (M) is provided by the lab: the number of items the oracle marks.
# Each Grover iteration rotates by 2θ with sin θ = √(M/N), so this count brings the angle close to π/2.
iterations = floor(pi / 4 * sqrt(N / num_marked))


def diffuser(qc):
    # Inversion about the mean: H·X, a Z controlled by all qubits (the phase flip of |0000⟩), then X·H.
    for qubit in range(4):
        qc.h(qubit)
        qc.x(qubit)
    # Z on qubit 3 controlled by qubits 0 to 2: a Hadamard, a multi-controlled NOT, a Hadamard.
    qc.h(3)
    qc.mcx([0, 1, 2], 3)
    qc.h(3)
    for qubit in range(4):
        qc.x(qubit)
        qc.h(qubit)


# Uniform superposition |s⟩: the same amplitude on every item.
for qubit in range(4):
    qc.h(qubit)

# One iteration: the oracle flips the sign of the marked items, the diffuser reflects about the mean.
for _ in range(iterations):
    oracle(qc)
    diffuser(qc)
