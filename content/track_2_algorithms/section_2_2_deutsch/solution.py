# Idea: with the auxiliary qubit in |−⟩ the oracle writes (−1)^f(x) on the input,
# and a final Hadamard turns the relative sign into 0 (constant) or 1 (balanced).
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
# Auxiliary qubit in |−⟩, so that the query kicks the phase (−1)^f(x) back onto the input.
qc.x(1)
qc.h(1)
# Input in |+⟩: both values of x are queried in the same call.
qc.h(0)

oracle(qc)

# Hadamard on the input: the amplitudes interfere, |+⟩ goes to |0⟩ and |−⟩ goes to |1⟩.
qc.h(0)
