from qiskit import QuantumCircuit

# Idea: the four Bell states differ from |Φ⁺⟩ by a Z and/or an X on one qubit, so build |Φ⁺⟩ and correct it with the bits of `bell`.
# The values 4 and 5 are product states, which also test the qubit-ordering convention.
qc = QuantumCircuit(2)
if bell < 4:
    # Hadamard on qubit 0 followed by CNOT (control 0, target 1) creates |Φ⁺⟩.
    qc.h(0)
    qc.cx(0, 1)
    if bell & 1:
        # Z on one qubit flips the sign of |11⟩: |Φ⁺⟩ becomes |Φ⁻⟩.
        qc.z(0)
    if bell & 2:
        # X on one qubit exchanges |00⟩ with |10⟩ and |11⟩ with |01⟩, giving |Ψ⁺⟩ (or |Ψ⁻⟩ together with Z).
        qc.x(1)
else:
    # In the label |q₁q₀⟩ the left bit is qubit 1: H on qubit 1 gives (|00⟩ + |10⟩)/√2, with qubit 0 in |0⟩.
    qc.h(1)
    if bell == 5:
        # X on qubit 0 puts the right bit in 1, giving (|01⟩ + |11⟩)/√2.
        qc.x(0)
