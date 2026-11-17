from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

# Qubit 0: the state to copy. Qubit 1: the blank qubit, in |0⟩.
qc = QuantumCircuit(2)

prepare_input(qc)  # |ψ⟩ on qubit 0; in the editor, |ψ⟩ = |+⟩

# 1. Copy qubit 0 onto qubit 1 with one CNOT.

# 2. Compare the output with the ideal copy |+⟩|+⟩:
#    copy_fidelity = state_fidelity(output, ideal)
