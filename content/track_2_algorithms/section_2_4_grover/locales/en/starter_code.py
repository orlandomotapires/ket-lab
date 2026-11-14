from qiskit import QuantumCircuit

qc = QuantumCircuit(4)


def diffuser(qc):
    # Inversion about the mean: H, X, multi-controlled Z, X, H.
    pass


# 1. Uniform superposition on the 4 qubits.
# 2. Grover iterations: oracle(qc) followed by diffuser(qc).
