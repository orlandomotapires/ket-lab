# Idea: the GHZ state can grow from any qubit, as long as each CNOT copies the branch from a qubit
# that already holds it onto a neighbor that does not. On this T the best start is the junction,
# qubit 1, because it touches three others: 4 CNOTs, one per new qubit, and no SWAP.
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

# The device: 5 qubits in a T. Edges are listed in one direction and made symmetric, because a
# CNOT can run either way between two connected qubits.
coupling_map = CouplingMap([(0, 1), (1, 2), (1, 3), (3, 4)])
coupling_map.make_symmetric()
basis_gates = ["rz", "sx", "x", "cx"]

# Hadamard on the junction, then one CNOT per edge, always from a qubit already in the state.
# A fan-out from qubit 0 would not work: its only neighbor is 1, and every other CNOT needs SWAPs.
ghz = QuantumCircuit(5)
ghz.h(1)
ghz.cx(1, 0)
ghz.cx(1, 2)
ghz.cx(1, 3)
ghz.cx(3, 4)

# The circuit already follows the edges, so the transpiler only rewrites h in the basis gates.
qc = transpile(ghz, coupling_map=coupling_map, basis_gates=basis_gates, optimization_level=1, seed_transpiler=7)
print(qc.count_ops(), "depth", qc.depth())
