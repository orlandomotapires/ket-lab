# Idea: write the phase (−1)^f(x) directly with Z and CZ gates, so no auxiliary qubit is needed.
from qiskit import QuantumCircuit

# f(x) = x0 ⊕ x1·x2, as a phase oracle: (-1)^f(x) = Z on qubit 0 times CZ on qubits 1 and 2.
qc = QuantumCircuit(3)
# Uniform superposition: every x is present with the same amplitude.
for qubit in range(3):
    qc.h(qubit)

# Z gives the sign (−1)^x0 and CZ gives (−1)^(x1·x2); together they give (−1)^f(x).
qc.z(0)
qc.cz(1, 2)

# Hadamards again: interference sends this balanced function away from |000⟩.
for qubit in range(3):
    qc.h(qubit)
