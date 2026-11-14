from qiskit import QuantumCircuit

# Qubit 0: control. Qubit 1: target.
qc = QuantumCircuit(2)

# 1. Target in |−⟩ and control in |+⟩.
# 2. CNOT from the control (0) to the target (1).
