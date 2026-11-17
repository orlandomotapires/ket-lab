from math import atan2
from qiskit import QuantumCircuit

# Idea: normalize (3, 4) to (0.6, 0.8), then let one R_y rotation set the polar angle θ with tan(θ/2) = β/α.
# The amplitudes are real, so the longitude is φ = 0 and no phase gate is needed.
qc = QuantumCircuit(1)
# R_y(θ)|0⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩. Taking θ = 2·atan2(4, 3) gives 0.6|0⟩ + 0.8|1⟩, which is already normalized.
qc.ry(2 * atan2(4, 3), 0)
