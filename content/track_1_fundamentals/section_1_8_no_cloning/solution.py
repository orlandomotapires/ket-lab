from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

# Idea: one CNOT copies |0⟩ and |1⟩, but by linearity it cannot copy |+⟩, and the fidelity with the ideal copy measures the failure.
qc = QuantumCircuit(2)
prepare_input(qc)

# CNOT with the blank qubit 1 as target: |00⟩ → |00⟩ and |10⟩ → |11⟩. On |+⟩ it gives the entangled state |Φ⁺⟩.
qc.cx(0, 1)

# Final state of the circuit, as a state vector.
output = Statevector(qc)
# The ideal copy of |+⟩ would be the product state |+⟩|+⟩ ("++" is the label of that state).
ideal_copy = Statevector.from_label("++")
# F = |⟨++|Φ⁺⟩|² = 1/2, so the CNOT copier fails for |+⟩.
copy_fidelity = state_fidelity(output, ideal_copy)
