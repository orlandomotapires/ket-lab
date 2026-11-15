from qiskit import QuantumCircuit
from qiskit.quantum_info import concurrence, partial_trace

# Qubits 0 and 1 form one Bell pair, qubits 2 and 3 the other.
# Qubits 1 and 2 are measured; qubits 0 and 3 never share a gate.
qc = QuantumCircuit(4, 2)

# 1. Create the pairs (0, 1) and (2, 3).
# 2. Record c_before, the concurrence of qubits (0, 3) at this point:
#    final_state(qc) returns the state vector of one run of qc, and
#    concurrence(partial_trace(state, [1, 2])) is the concurrence of qubits 0 and 3.
# 3. Bell measurement of qubits 1 and 2, with the results in the classical bits.
# 4. Classically controlled corrections on qubit 3.
# 5. Record c_after in the same way.

c_before = None
c_after = None
