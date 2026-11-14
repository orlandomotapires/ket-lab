from qiskit import QuantumCircuit

# Qubits 0 a 2: contagem. Qubit 3: autovetor de U. 3 bits para a medição.
qc = QuantumCircuit(4, 3)

# 1. Prepare o autovetor e a superposição na contagem.
# 2. Potências controladas: apply_controlled_u(qc, controle, potência).
# 3. inverse_qft(qc, [0, 1, 2]) e medição da contagem.

# 4. Leia o resultado e estime a fase.
theta = None
