# Idea: one query followed by Hadamards makes every outcome y orthogonal to s (y·s = 0 mod 2).
# Collect a few outcomes, then keep the nonzero string that is orthogonal to all of them.
from qiskit import QuantumCircuit

qc = QuantumCircuit(6, 3)
# Uniform superposition on the input register; the output register stays in |000⟩.
for qubit in range(3):
    qc.h(qubit)

oracle(qc)

# Second Hadamard layer: only the strings y with y·s = 0 keep amplitude, each equally likely.
for qubit in range(3):
    qc.h(qubit)
qc.measure([0, 1, 2], [0, 1, 2])

counts = run_shots(qc)


def dot(a, b):
    """Inner product of two bit strings, modulo 2."""
    return bin(int(a, 2) & int(b, 2)).count("1") % 2


# Every nonzero string orthogonal to all the outcomes solves the system y·s = 0.
# If none exists, the outcomes span all of {0,1}^3 and only s = 000 remains.
solutions = [s for s in ("001", "010", "011", "100", "101", "110", "111")
             if all(dot(y, s) == 0 for y in counts)]
s_found = solutions[0] if len(solutions) == 1 else "000"
