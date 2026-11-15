from qiskit import QuantumCircuit

qc = QuantumCircuit(4)
for qubit in range(4):
    qc.h(qubit)

phase_oracle(qc)

for qubit in range(4):
    qc.h(qubit)
