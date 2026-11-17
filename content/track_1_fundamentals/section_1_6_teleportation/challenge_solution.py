from qiskit import QuantumCircuit

# Idea: move every measurement to the end (deferred measurement), so each classically controlled gate becomes a controlled gate.
qc = QuantumCircuit(3)
prepare_alice_state(qc)

# Bell pair shared by Alice (qubit 1) and Bob (qubit 2).
qc.h(1)
qc.cx(1, 2)

# Alice's Bell-basis change on qubits 0 and 1, with no measurement after it.
qc.cx(0, 1)
qc.h(0)

# Deferred measurement: the classical controls become quantum controls.
# X on Bob's qubit if qubit 1 is 1, and Z if qubit 0 is 1, as in the measured version.
qc.cx(1, 2)
qc.cz(0, 2)
