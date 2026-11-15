from qiskit import QuantumCircuit

qc = QuantumCircuit(5, 3)
for qubit in range(3):
    qc.h(qubit)

oracle(qc)

for qubit in range(3):
    qc.h(qubit)
qc.measure([0, 1, 2], [0, 1, 2])

counts = run_shots(qc)


def dot(a, b):
    return bin(int(a, 2) & int(b, 2)).count("1") % 2


solutions = [s for s in ("001", "010", "011", "100", "101", "110", "111")
             if all(dot(y, s) == 0 for y in counts)]
s_found = solutions[0] if len(solutions) == 1 else "000"
