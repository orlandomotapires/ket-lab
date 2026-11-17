from qiskit import QuantumCircuit

# Idea: a computational-basis measurement cannot see the sign between |0⟩ and |1⟩, so turn that sign into a pole first.
qc = QuantumCircuit(1, 1)
prepare_unknown(qc)

# H|+⟩ = |0⟩ and H|−⟩ = |1⟩: the two terms of |1⟩ cancel for |+⟩ and the two terms of |0⟩ cancel for |−⟩.
qc.h(0)
# Now the outcome is certain: 0 for |+⟩ and 1 for |−⟩ (a measurement in the X basis).
qc.measure(0, 0)
