from qiskit import QuantumCircuit

# Qubit 0: Alice's state. Qubit 1: Alice's half of the pair. Qubit 2: Bob's half.
# Two classical bits store the results of Alice's measurements.
qc = QuantumCircuit(3, 2)

prepare_alice_state(qc)  # |ψ⟩ on qubit 0, unknown

# 1. Create a Bell pair on qubits 1 and 2.
# 2. Alice: CNOT from 0 to 1, H on qubit 0, measure qubits 0 and 1.
# 3. Bob: apply corrections conditioned on the measured bits.
