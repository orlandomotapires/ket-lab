# Idea: with the target in |−⟩ (an eigenstate of X), the CNOT does not change the target.
# It kicks the eigenvalue −1 back onto the control as a relative phase.
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
# X then H on the target: |0⟩ → |1⟩ → |−⟩, the eigenstate of X with eigenvalue −1.
qc.x(1)
qc.h(1)
# Hadamard on the control: |+⟩ has amplitude on both |0⟩ and |1⟩, so the phase can show.
qc.h(0)
# CNOT last: the control's |1⟩ term gets the factor −1, turning |+⟩ into |−⟩.
qc.cx(0, 1)
