# Idea: the oracle writes the phase (−1)^(s·x), which is exactly H^⊗n|s⟩,
# so one more layer of Hadamards turns the register into |s⟩.
from qiskit import QuantumCircuit

qc = QuantumCircuit(5)
# Auxiliary qubit in |−⟩, so that each CNOT of the oracle kicks a sign back onto its input qubit.
qc.x(4)
qc.h(4)
# Uniform superposition on the four input qubits.
for qubit in range(4):
    qc.h(qubit)

oracle(qc)

# The register is now H^⊗4|s⟩. H is its own inverse, so this layer returns |s⟩.
for qubit in range(4):
    qc.h(qubit)
