from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

coupling_map = CouplingMap.from_line(4)
basis_gates = ["rz", "sx", "x", "cx"]

# Each CNOT acts on neighbors of the line, so no SWAP is needed.
ghz = QuantumCircuit(4)
ghz.h(0)
ghz.cx(0, 1)
ghz.cx(1, 2)
ghz.cx(2, 3)

qc = transpile(ghz, coupling_map=coupling_map, basis_gates=basis_gates, optimization_level=1, seed_transpiler=7)

print(qc.count_ops(), "depth", qc.depth())
