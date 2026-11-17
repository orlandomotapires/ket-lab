# Idea: handle one qubit at a time from the most significant. A Hadamard puts it on the equator
# and controlled phases from the lower qubits add the fractions of a turn that encode x.
from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
prepare_input(qc)

# Qubit 2: Hadamard, then π/2 controlled by qubit 1 and π/4 controlled by qubit 0 (phase x/8 of a turn).
qc.h(2)
qc.cp(pi / 2, 1, 2)
qc.cp(pi / 4, 0, 2)
# Qubit 1: Hadamard, then π/2 controlled by qubit 0 (phase x/4 of a turn).
qc.h(1)
qc.cp(pi / 2, 0, 1)
# Qubit 0: only a Hadamard is left (phase x/2 of a turn).
qc.h(0)
# These steps leave the phases in reverse qubit order, so swap qubits 0 and 2 to fix the output order.
qc.swap(0, 2)
