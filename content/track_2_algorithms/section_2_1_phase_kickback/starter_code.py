from qiskit import QuantumCircuit

# Qubit 0: control. Qubit 1: target.
qc = QuantumCircuit(2)

# 1. Prepare the target in |−⟩ and the control in |+⟩.
# 2. Apply a CNOT with control 0 and target 1.
