from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
prepare_alice_state(qc)

qc.h(1)
qc.cx(1, 2)

qc.cx(0, 1)
qc.h(0)

# Deferred measurement: the classical controls become quantum controls.
qc.cx(1, 2)
qc.cz(0, 2)
