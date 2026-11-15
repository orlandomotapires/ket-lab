from qiskit import QuantumCircuit
from qiskit.quantum_info import concurrence, partial_trace

qc = QuantumCircuit(4, 2)

# Two Bell pairs: (0, 1) and (2, 3).
qc.h(0)
qc.cx(0, 1)
qc.h(2)
qc.cx(2, 3)

state_before = final_state(qc)
c_before = float(concurrence(partial_trace(state_before, [1, 2])))

# Bell measurement on the middle qubits 1 and 2.
qc.cx(1, 2)
qc.h(1)
qc.measure(1, 0)
qc.measure(2, 1)

# Corrections on qubit 3, conditioned on the two bits.
with qc.if_test((qc.clbits[1], 1)):
    qc.x(3)
with qc.if_test((qc.clbits[0], 1)):
    qc.z(3)

state_after = final_state(qc)
c_after = float(concurrence(partial_trace(state_after, [1, 2])))
