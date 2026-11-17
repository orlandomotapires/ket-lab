from math import pi
from qiskit import QuantumCircuit

# Idea: give up exact copies of |1⟩ to get good copies on the equator, with |0⟩|0⟩ → |00⟩ and |1⟩|0⟩ → (|01⟩ + |10⟩)/√2.
qc = QuantumCircuit(2)
prepare_input(qc)

# Phase-covariant cloner, in two steps.
# Controlled R_y(π/2) acts on the blank qubit only when qubit 0 is 1, turning |1⟩|0⟩ into |1⟩(|0⟩ + |1⟩)/√2.
qc.cry(pi / 2, 0, 1)
# CNOT from qubit 1 to qubit 0 turns the |11⟩ term into |01⟩ (kets written qubit 0 first), leaving (|01⟩ + |10⟩)/√2; |00⟩ is untouched.
qc.cx(1, 0)
