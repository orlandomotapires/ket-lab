from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

qc = QuantumCircuit(2)
prepare_input(qc)

qc.cx(0, 1)

output = Statevector(qc)
ideal_copy = Statevector.from_label("++")
copy_fidelity = state_fidelity(output, ideal_copy)
