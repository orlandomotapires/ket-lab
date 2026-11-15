from qiskit import QuantumCircuit

qc = QuantumCircuit(1, 1)
prepare_unknown(qc)

qc.sdg(0)
qc.h(0)
qc.measure(0, 0)
