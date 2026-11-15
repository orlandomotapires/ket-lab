from math import floor, pi, sqrt

from qiskit import QuantumCircuit

# f(a, b, c) = (a OR b) AND (NOT a OR c) AND (NOT b OR NOT c), with a, b, c = qubits 0, 1, 2.
# Truth table: only (a, b, c) = (0, 1, 0) and (1, 0, 1) satisfy all three clauses.
# Printed as the bit string "c b a" these are "010" and "101".


def oracle(qc):
    for solution in ("010", "101"):
        zeros = [qubit for qubit, bit in enumerate(reversed(solution)) if bit == "0"]
        for qubit in zeros:
            qc.x(qubit)
        qc.h(2)
        qc.ccx(0, 1, 2)
        qc.h(2)
        for qubit in zeros:
            qc.x(qubit)


def diffuser(qc):
    for qubit in range(3):
        qc.h(qubit)
        qc.x(qubit)
    qc.h(2)
    qc.ccx(0, 1, 2)
    qc.h(2)
    for qubit in range(3):
        qc.x(qubit)
        qc.h(qubit)


N = 8
M = 2
iterations = floor(pi / 4 * sqrt(N / M))

qc = QuantumCircuit(5, 3)
for qubit in range(3):
    qc.h(qubit)
for _ in range(iterations):
    oracle(qc)
    diffuser(qc)
qc.measure([0, 1, 2], [0, 1, 2])

counts = run_shots(qc, 1024)
solutions = sorted(key for key, count in counts.items() if count > 1024 * 0.2)
