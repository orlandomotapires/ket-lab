from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
prepare_input(qc)  # input |x⟩; here, |101⟩ = |5⟩

# QFT: Hadamards, controlled phases (qc.cp) and a final swap.
