from qiskit import QuantumCircuit

# Idea: an equal superposition on each qubit makes all 8 outcomes equally likely, and measuring reads them out.
qc = QuantumCircuit(3, 3)
# Hadamard on every qubit: each goes to |+⟩, so the three bits are fair and independent.
for q in range(3):
    qc.h(q)
# Measure qubit q into classical bit q, so the bit string follows the qubit labels.
for q in range(3):
    qc.measure(q, q)
