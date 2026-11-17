from qiskit import QuantumCircuit

# Idea: Alice's Bell-basis measurement leaves Bob's qubit in |ψ⟩ altered by a known Pauli, and two classical bits say which one.
qc = QuantumCircuit(3, 2)
prepare_alice_state(qc)

# Bell pair on qubits 1 and 2: Alice keeps qubit 1 and Bob holds qubit 2.
qc.h(1)
qc.cx(1, 2)

# CNOT then H on Alice's two qubits changes from the Bell basis to the computational basis, so measuring them is a Bell measurement.
qc.cx(0, 1)
qc.h(0)
# Each result is one bit that Alice sends to Bob; the measurement also destroys her copy of |ψ⟩.
qc.measure(0, 0)
qc.measure(1, 1)

# The bit from qubit 1 says that Bob's state has its |0⟩ and |1⟩ amplitudes exchanged, which X undoes.
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
# The bit from qubit 0 says that the sign of the |1⟩ amplitude is flipped, which Z undoes.
with qc.if_test((qc.clbits[0], 1)):
    qc.z(2)
