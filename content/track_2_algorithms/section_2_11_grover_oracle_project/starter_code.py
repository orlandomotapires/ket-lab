from math import floor, pi, sqrt

from qiskit import QuantumCircuit

# Search qubits: 0, 1, 2 are the variables a, b, c of the formula
#   f(a, b, c) = (a OR b) AND (NOT a OR c) AND (NOT b OR NOT c).
# Qubits 3 and 4 are ancillas that start in |0> and must end in |0>.
# A result is printed as the bit string "c b a" (qubit 0 on the right).


def oracle(qc):
    # Flip the sign of every state that satisfies f, using qubits 0 to 4.
    pass


def diffuser(qc):
    # Inversion about the mean on qubits 0, 1, 2.
    pass


N = 8
M = 0  # the number of strings that satisfy f
iterations = 0  # the optimal number of Grover iterations for N and M

qc = QuantumCircuit(5, 3)
# Uniform superposition on qubits 0, 1, 2; then `iterations` times oracle and diffuser;
# then measure qubits 0, 1, 2 into the classical bits 0, 1, 2.

# counts = run_shots(qc, 1024)
solutions = []  # the bit strings found, for example ["010", "101"]
