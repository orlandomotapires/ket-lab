from qiskit import QuantumCircuit

N = 16
qc = QuantumCircuit(4)

# num_marked (M) é fornecido pelo laboratório: quantos itens o oráculo marca.
iterations = 0  # calcule a partir de N e num_marked


def diffuser(qc):
    # Inversão em torno da média: H, X, Z multicontrolada, X, H.
    pass


# 1. Superposição uniforme nos 4 qubits.
# 2. Iterações de Grover: oracle(qc) seguido de diffuser(qc).
