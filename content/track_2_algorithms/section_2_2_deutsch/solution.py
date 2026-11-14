from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.x(1)
qc.h(1)
qc.h(0)

oracle(qc)

qc.h(0)
