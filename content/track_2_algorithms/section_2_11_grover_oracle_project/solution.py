# Idea: list the satisfying strings by hand, mark each one with a multi-controlled Z, and run
# Grover with the iteration count for eight items and two solutions (one iteration reaches probability 1).
from math import floor, pi, sqrt

from qiskit import QuantumCircuit

# f(a, b, c) = (a OR b) AND (NOT a OR c) AND (NOT b OR NOT c), with a, b, c = qubits 0, 1, 2.
# Truth table: only (a, b, c) = (0, 1, 0) and (1, 0, 1) satisfy all three clauses.
# Printed as the bit string "c b a" these are "010" and "101".


def oracle(qc):
    for solution in ("010", "101"):
        # X on the qubits that are 0 in the solution, so the solution becomes |111⟩.
        zeros = [qubit for qubit, bit in enumerate(reversed(solution)) if bit == "0"]
        for qubit in zeros:
            qc.x(qubit)
        # Controlled-controlled-Z flips the sign of |111⟩ only, which is the solution after the X gates.
        qc.h(2)
        qc.ccx(0, 1, 2)
        qc.h(2)
        # Undo the X gates, so that no other state is changed.
        for qubit in zeros:
            qc.x(qubit)


def diffuser(qc):
    # Inversion about the mean on three qubits: H·X, a controlled-controlled-Z, then X·H.
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
# sin θ = √(M/N) = 1/2, so θ = 30° and one iteration rotates the state to 90°.
iterations = floor(pi / 4 * sqrt(N / M))

qc = QuantumCircuit(5, 3)
# Uniform superposition on the three variable qubits; the ancillas stay in |0⟩.
for qubit in range(3):
    qc.h(qubit)
# Each iteration: the oracle marks the solutions, the diffuser amplifies them.
for _ in range(iterations):
    oracle(qc)
    diffuser(qc)
qc.measure([0, 1, 2], [0, 1, 2])

counts = run_shots(qc, 1024)
# The two solutions each appear about half the time; keep the strings above 20% of the shots.
solutions = sorted(key for key, count in counts.items() if count > 1024 * 0.2)
