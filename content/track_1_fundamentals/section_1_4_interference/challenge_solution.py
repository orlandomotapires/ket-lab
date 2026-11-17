from qiskit import QuantumCircuit

# Idea: rotate the Y axis onto the X axis with S†, then use the Hadamard as in the X-basis measurement.
qc = QuantumCircuit(1, 1)
prepare_unknown(qc)

# S† is a −90° turn about Z: |+i⟩ goes to |+⟩ and |−i⟩ goes to |−⟩.
qc.sdg(0)
# H sends |+⟩ to |0⟩ and |−⟩ to |1⟩, so |+i⟩ gives 0 and |−i⟩ gives 1.
qc.h(0)
# Measure in the computational basis: the whole sequence is a measurement in the Y basis.
qc.measure(0, 0)
