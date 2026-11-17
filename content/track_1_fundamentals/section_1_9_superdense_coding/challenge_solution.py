from qiskit import QuantumCircuit

# Idea: the shared pair is now |Ψ⁻⟩, so Alice's Paulis must be relabeled; Bob's decoding stays the same.
qc = QuantumCircuit(2)

# Shared pair |Ψ⁻⟩ = (|01⟩ − |10⟩)/√2: X on both qubits gives |11⟩, then H and CNOT make the pair.
qc.x(0)
qc.x(1)
qc.h(0)
qc.cx(0, 1)

# Alice, on qubit 1 only. With no gate from Alice, Bob would decode 11, so the rule is flipped, a 0 bit triggers the gate:
# Z turns |Ψ⁻⟩ into |Ψ⁺⟩ (decoded as 01) and X turns it into |Φ⁻⟩ (decoded as 10), so a "0" bit now triggers the gate.
if message[0] == "0":
    qc.z(1)
if message[1] == "0":
    qc.x(1)

# Bob's decoding is unchanged: CNOT from 1 to 0, then H on qubit 1.
qc.cx(1, 0)
qc.h(1)
