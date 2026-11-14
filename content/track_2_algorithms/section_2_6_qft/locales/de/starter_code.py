from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
prepare_input(qc)  # Eingabe |x⟩; hier |101⟩ = |5⟩

# QFT: Hadamards, kontrollierte Phasen (qc.cp) und ein abschließender Swap.
