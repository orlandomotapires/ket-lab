from qiskit import QuantumCircuit

qc = QuantumCircuit(1, 1)
prepare_unknown(qc)

qc.h(0)
qc.measure(0, 0)
