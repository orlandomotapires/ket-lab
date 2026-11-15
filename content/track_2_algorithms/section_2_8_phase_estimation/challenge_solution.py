from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 3)
qc.x(3)
for qubit in range(3):
    qc.h(qubit)
for j in range(3):
    apply_controlled_u(qc, j, 2**j)
inverse_qft(qc, [0, 1, 2])
qc.measure([0, 1, 2], [0, 1, 2])

counts = run_shots(qc, 4096)
best = max(counts, key=counts.get)
theta = int(best, 2) / 8
p_best = counts[best] / 4096
