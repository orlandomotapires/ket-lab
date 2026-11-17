from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

# The device: 4 qubits in a line, 0 - 1 - 2 - 3. A two-qubit gate needs two neighbors.
coupling_map = CouplingMap.from_line(4)
# The only gates the device runs.
basis_gates = ["rz", "sx", "x", "cx"]

# A 4-qubit GHZ state, (|0000⟩ + |1111⟩)/√2.
ghz = QuantumCircuit(4)
ghz.h(0)
ghz.cx(0, 1)
ghz.cx(0, 2)
ghz.cx(0, 3)

# The circuit that would run on the device.
qc = transpile(ghz, coupling_map=coupling_map, basis_gates=basis_gates, optimization_level=1, seed_transpiler=7)

print(qc.count_ops(), "depth", qc.depth())
