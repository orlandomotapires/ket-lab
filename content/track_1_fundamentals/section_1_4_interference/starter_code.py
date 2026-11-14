from qiskit import QuantumCircuit

qc = QuantumCircuit(1, 1)
prepare_unknown(qc)  # |+⟩ or |−⟩, unknown which

# Mission: add gates and a measurement so that |+⟩ always gives 0
# and |−⟩ always gives 1.
