from qiskit import QuantumCircuit

# Qubit 0: Alice. Qubit 1: Alices Hälfte des Paares. Qubit 2: Bob.
# 2 klassische Bits für die Ergebnisse von Alices Messungen.
qc = QuantumCircuit(3, 2)

prepare_alice_state(qc)  # |ψ⟩ auf Qubit 0; du weißt nicht, welcher es ist

# 1. Erzeuge das Bell-Paar zwischen den Qubits 1 und 2.
# 2. Alice: CNOT von 0 nach 1, H auf Qubit 0, die Qubits 0 und 1 messen.
# 3. Bob: Korrekturen, abhängig von den gemessenen Bits.
