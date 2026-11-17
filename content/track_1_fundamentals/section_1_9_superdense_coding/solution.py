from qiskit import QuantumCircuit

# Idea: Alice's Pauli on her half of |Φ⁺⟩ picks one of four orthogonal Bell states, and Bob reads it by undoing the Bell pair.
qc = QuantumCircuit(2)

# Shared pair |Φ⁺⟩ = (|00⟩ + |11⟩)/√2: Alice holds qubit 1 and Bob holds qubit 0.
qc.h(0)
qc.cx(0, 1)

# Z flips the sign of |11⟩, so the first message bit selects |Φ⁻⟩ or |Ψ⁻⟩ (the minus-sign states).
if message[0] == "1":
    qc.z(1)
# X exchanges |00⟩ with |10⟩ and |11⟩ with |01⟩, so the second bit selects |Ψ⁺⟩ or |Ψ⁻⟩. Only qubit 1, which Alice owns, is touched.
if message[1] == "1":
    qc.x(1)

# Bob's decoding, the same for every message: CNOT then H on qubit 1 maps the Bell basis to the computational basis.
qc.cx(1, 0)
qc.h(1)
