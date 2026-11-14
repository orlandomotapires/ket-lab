from qiskit import QuantumCircuit

# Qubit 0: Alice. Qubit 1: Alice's half of the pair. Qubit 2: Bob.
# 2 classical bits for the results of Alice's measurements.
qc = QuantumCircuit(3, 2)

prepare_alice_state(qc)  # |ψ⟩ on qubit 0; you do not know which one it is

# 1. Create the Bell pair between qubits 1 and 2.
# 2. Alice: CNOT from 0 to 1, H on qubit 0, measure qubits 0 and 1.
# 3. Bob: corrections conditioned on the measured bits.
