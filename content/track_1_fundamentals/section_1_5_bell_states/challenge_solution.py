from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
if bell & 1:
    qc.z(0)
if bell & 2:
    qc.x(1)
