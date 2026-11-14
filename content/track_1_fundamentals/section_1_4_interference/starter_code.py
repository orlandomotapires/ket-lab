from qiskit import QuantumCircuit

qc = QuantumCircuit(1, 1)
prepare_unknown(qc)  # |+⟩ or |−⟩, you do not know which

# Your mission: add gates and a measurement so that |+⟩ always gives 0
# and |−⟩ always gives 1.
