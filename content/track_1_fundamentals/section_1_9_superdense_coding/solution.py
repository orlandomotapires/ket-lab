from qiskit import QuantumCircuit

qc = QuantumCircuit(2)

qc.h(0)
qc.cx(0, 1)

if message[0] == "1":
    qc.z(1)
if message[1] == "1":
    qc.x(1)

qc.cx(1, 0)
qc.h(1)
