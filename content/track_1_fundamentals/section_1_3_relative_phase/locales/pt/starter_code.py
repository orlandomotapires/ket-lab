from qiskit import QuantumCircuit

qc = QuantumCircuit(1)
prepare_input(qc)  # um estado desconhecido no qubit 0

# Uma sequência de portas já foi aplicada:
qc.x(0)
qc.h(0)
qc.s(0)
qc.t(0)
qc.h(0)

# Sua missão: acrescente portas para o qubit voltar ao estado de entrada,
# seja ele qual for.
