from math import floor, pi, sqrt

from qiskit import QuantumCircuit

N = 16
qc = QuantumCircuit(4)

# num_marked (M) vem do laboratório: quantos itens o oráculo marca.
iterations = floor(pi / 4 * sqrt(N / num_marked))


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
