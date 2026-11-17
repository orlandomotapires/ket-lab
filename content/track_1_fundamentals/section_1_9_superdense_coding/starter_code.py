from qiskit import QuantumCircuit

# Qubit 1: Alice's half of the pair. Qubit 0: Bob's half.
# `message` is Alice's two-bit message, a string such as "10".
qc = QuantumCircuit(2)

# 1. Create the shared Bell pair |Φ+⟩: H on qubit 0, then CNOT from 0 to 1.

# 2. Alice acts on qubit 1 only: Z if message[0] == "1", X if message[1] == "1".

# 3. Bob decodes: CNOT from 1 to 0, then H on qubit 1.
#    Reading |q1 q0⟩ then gives the message.
