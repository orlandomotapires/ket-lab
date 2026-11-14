from qiskit import QuantumCircuit

qc = QuantumCircuit(4)
qc.x(3)
qc.h(3)
for qubit in range(3):
    qc.h(qubit)

oracle(qc)

for qubit in range(3):
    qc.h(qubit)
