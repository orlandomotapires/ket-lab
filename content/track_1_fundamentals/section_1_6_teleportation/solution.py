from qiskit import QuantumCircuit

qc = QuantumCircuit(3, 2)
prepare_alice_state(qc)

qc.h(1)
qc.cx(1, 2)

qc.cx(0, 1)
qc.h(0)
qc.measure(0, 0)
qc.measure(1, 1)

with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
with qc.if_test((qc.clbits[0], 1)):
    qc.z(2)
