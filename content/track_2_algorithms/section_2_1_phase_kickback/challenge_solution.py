# Idea: |1⟩ is an eigenstate of the S gate with eigenvalue i, so a controlled-S kicks the phase i
# back onto the control. Controlled-S is cp with angle π/2.
from math import pi

from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
# Target in |1⟩: the eigenstate of S whose eigenvalue e^{iπ/2} = i is the phase to kick back.
qc.x(1)
# Control in |+⟩, so the kicked phase becomes a relative phase between |0⟩ and |1⟩.
qc.h(0)
# Controlled phase π/2: multiplies only the |1⟩|1⟩ component by i, giving (|0⟩ + i|1⟩)/√2 on the control.
qc.cp(pi / 2, 0, 1)
