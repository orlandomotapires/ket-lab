from qiskit import QuantumCircuit

qc = QuantumCircuit(1)
prepare_input(qc)

qc.x(0)
qc.h(0)
qc.s(0)
qc.t(0)
qc.h(0)

# Desfaz tudo: os inversos, na ordem contrária.
qc.h(0)
qc.tdg(0)
qc.sdg(0)
qc.h(0)
qc.x(0)
