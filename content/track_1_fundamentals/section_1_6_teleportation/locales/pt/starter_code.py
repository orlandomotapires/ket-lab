from qiskit import QuantumCircuit

# Qubit 0: Alice. Qubit 1: metade do par de Alice. Qubit 2: Bob.
# 2 bits clássicos para os resultados das medições de Alice.
qc = QuantumCircuit(3, 2)

prepare_alice_state(qc)  # |ψ⟩ no qubit 0; você não sabe qual é

# 1. Crie o par de Bell entre os qubits 1 e 2.
# 2. Alice: CNOT de 0 para 1, H no qubit 0, medir os qubits 0 e 1.
# 3. Bob: correções condicionadas aos bits medidos.
