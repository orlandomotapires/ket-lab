from qiskit import QuantumCircuit

# Idea: put the control in superposition, then let a CNOT copy that choice onto the target, which entangles the pair.
qc = QuantumCircuit(2)
# H on qubit 0 gives (|0⟩ + |1⟩)/√2 ⊗ |0⟩ = (|00⟩ + |01⟩)/√2 in the label |q₁q₀⟩.
qc.h(0)
# CNOT with control 0 flips qubit 1 only in the |1⟩ branch: (|00⟩ + |11⟩)/√2 = |Φ⁺⟩.
qc.cx(0, 1)
