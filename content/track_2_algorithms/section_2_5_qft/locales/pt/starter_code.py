from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
prepare_input(qc)  # entrada |x⟩; aqui, |101⟩ = |5⟩

# QFT: Hadamards, fases controladas (qc.cp) e um swap final.
