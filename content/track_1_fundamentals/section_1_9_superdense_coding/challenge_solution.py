from qiskit import QuantumCircuit

qc = QuantumCircuit(2)

# Shared pair |Ψ-> = (|01> - |10>)/sqrt(2)
qc.x(0)
qc.x(1)
qc.h(0)
qc.cx(0, 1)

# Alice, on qubit 1 only
if message[0] == "0":
    qc.z(1)
if message[1] == "0":
    qc.x(1)

# Bob's decoding is unchanged
qc.cx(1, 0)
qc.h(1)
