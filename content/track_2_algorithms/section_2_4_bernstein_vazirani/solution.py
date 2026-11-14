from qiskit import QuantumCircuit

qc = QuantumCircuit(5)
qc.x(4)
qc.h(4)
for qubit in range(4):
    qc.h(qubit)

oracle(qc)

for qubit in range(4):
    qc.h(qubit)
