from qiskit import QuantumCircuit

qc = QuantumCircuit(4)


def diffuser(qc):
    # Inversão em torno da média: H, X, Z multicontrolada, X, H.
    pass


# 1. Superposição uniforme nos 4 qubits.
# 2. Iterações de Grover: oracle(qc) seguido de diffuser(qc).
