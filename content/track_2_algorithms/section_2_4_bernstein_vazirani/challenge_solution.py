# Idea: the phase oracle already writes (−1)^(s·x), so the circuit needs no auxiliary qubit.
from qiskit import QuantumCircuit

qc = QuantumCircuit(4)
# Uniform superposition on the input register.
for qubit in range(4):
    qc.h(qubit)

phase_oracle(qc)

# The register is H^⊗4|s⟩ up to a global phase, and a second layer of Hadamards returns |s⟩.
for qubit in range(4):
    qc.h(qubit)
