from qiskit import QuantumCircuit

# Qubit 0: controle. Qubit 1: alvo.
qc = QuantumCircuit(2)

# 1. Alvo em |−⟩ e controle em |+⟩.
# 2. CNOT do controle (0) para o alvo (1).
