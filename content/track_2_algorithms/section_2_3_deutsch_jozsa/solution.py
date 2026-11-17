# Idea: the Deutsch–Jozsa circuit. The oracle writes (−1)^f(x) on every input state, and the final
# Hadamards map the average of those signs to |0…0⟩ (constant) or away from it (balanced).
from qiskit import QuantumCircuit

qc = QuantumCircuit(4)
# Auxiliary qubit in |−⟩, so that the query kicks the phase (−1)^f(x) back onto the input register.
qc.x(3)
qc.h(3)
# Uniform superposition on the input register: one query reaches every x.
for qubit in range(3):
    qc.h(qubit)

oracle(qc)

# Hadamards again: the amplitude of |000⟩ becomes the average of the signs, ±1 or 0.
for qubit in range(3):
    qc.h(qubit)
