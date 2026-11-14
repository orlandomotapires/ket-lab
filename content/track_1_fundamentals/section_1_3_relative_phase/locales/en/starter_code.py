from qiskit import QuantumCircuit

qc = QuantumCircuit(1)
qc.h(0)  # prepares |+⟩, on the equator of the sphere

# Your mission: rotate a quarter turn around Z, to the +Y point.
