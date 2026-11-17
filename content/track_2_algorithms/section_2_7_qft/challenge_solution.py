# Idea: the inverse QFT is the QFT circuit run backwards with every gate inverted.
# Hadamards and swaps are their own inverses, and the controlled phases change sign.
from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
prepare_input(qc)

# Inverse QFT: the gates of the QFT in reverse order, each one inverted.
# The swap came last in the QFT, so it comes first here.
qc.swap(0, 2)
# Qubit 0 first, then qubit 1, then qubit 2: the reverse of the order in the QFT.
qc.h(0)
qc.cp(-pi / 2, 0, 1)
qc.h(1)
# Qubit 2: undo the π/4 phase from qubit 0 and the π/2 phase from qubit 1, then its Hadamard.
qc.cp(-pi / 4, 0, 2)
qc.cp(-pi / 2, 1, 2)
qc.h(2)
