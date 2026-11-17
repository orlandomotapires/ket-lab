from qiskit import QuantumCircuit

N = 16
qc = QuantumCircuit(4)

# num_marked (M) is provided by the lab: the number of items the oracle marks.
iterations = 0  # compute it from N and num_marked


def diffuser(qc):
    # Inversion about the mean: H, X, multi-controlled Z, X, H.
    pass


# 1. Uniform superposition on the 4 qubits.
# 2. Grover iterations: oracle(qc) followed by diffuser(qc).
