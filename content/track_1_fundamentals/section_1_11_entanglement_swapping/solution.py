from qiskit import QuantumCircuit
from qiskit.quantum_info import concurrence, partial_trace

# Idea: a Bell measurement on the two middle qubits projects the outer qubits onto a Bell state, and teleportation-style corrections fix which one.
qc = QuantumCircuit(4, 2)

# Two Bell pairs: (0, 1) and (2, 3).
# Each pair is |Φ⁺⟩, so qubits 0 and 3 are still in a product state.
qc.h(0)
qc.cx(0, 1)
qc.h(2)
qc.cx(2, 3)

# Reduced state of qubits 0 and 3 (trace out 1 and 2): a product state, so the concurrence is 0.
state_before = final_state(qc)
c_before = float(concurrence(partial_trace(state_before, [1, 2])))

# Bell measurement on the middle qubits 1 and 2: CNOT and H change to the computational basis, and measuring then
# projects qubits 0 and 3 onto one of the four Bell states without any gate acting on them.
qc.cx(1, 2)
qc.h(1)
qc.measure(1, 0)
qc.measure(2, 1)

# Corrections on qubit 3, conditioned on the two bits, as in teleportation.
# X undoes the exchange of |0⟩ and |1⟩ signaled by the bit of qubit 2.
with qc.if_test((qc.clbits[1], 1)):
    qc.x(3)
# Z undoes the sign flip signaled by the bit of qubit 1, so every branch ends in |Φ⁺⟩.
with qc.if_test((qc.clbits[0], 1)):
    qc.z(3)

# Same reduced state at the end: |Φ⁺⟩, with concurrence 1.
state_after = final_state(qc)
c_after = float(concurrence(partial_trace(state_after, [1, 2])))
