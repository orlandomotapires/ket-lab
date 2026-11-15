from qiskit import QuantumCircuit

# f(x) = x0 ⊕ x1·x2, as a phase oracle: (-1)^f(x) = Z on qubit 0 times CZ on qubits 1 and 2.
qc = QuantumCircuit(3)
for qubit in range(3):
    qc.h(qubit)

qc.z(0)
qc.cz(1, 2)

for qubit in range(3):
    qc.h(qubit)
