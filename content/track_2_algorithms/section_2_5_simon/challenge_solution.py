# Idea: the circuit and the post-processing are the same as in Simon's problem with n output qubits.
# Only the output register is smaller, because f has 2 output bits.
from qiskit import QuantumCircuit

qc = QuantumCircuit(5, 3)
# Uniform superposition on the three input qubits; qubits 3 and 4 hold f(x).
for qubit in range(3):
    qc.h(qubit)

oracle(qc)

# Second Hadamard layer: every outcome y satisfies y·s = 0 (mod 2).
for qubit in range(3):
    qc.h(qubit)
qc.measure([0, 1, 2], [0, 1, 2])

counts = run_shots(qc)


def dot(a, b):
    return bin(int(a, 2) & int(b, 2)).count("1") % 2


# s is nonzero here, so exactly one nonzero string is orthogonal to all outcomes once they span a plane.
solutions = [s for s in ("001", "010", "011", "100", "101", "110", "111")
             if all(dot(y, s) == 0 for y in counts)]
s_found = solutions[0] if len(solutions) == 1 else "000"
