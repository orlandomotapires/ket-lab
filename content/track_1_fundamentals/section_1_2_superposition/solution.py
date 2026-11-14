from qiskit import QuantumCircuit

qc = QuantumCircuit(3, 3)
for q in range(3):
    qc.h(q)
for q in range(3):
    qc.measure(q, q)
