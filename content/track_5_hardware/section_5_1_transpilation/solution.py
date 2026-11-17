# Idea: transpile does not change the circuit's structure, so write a GHZ circuit whose CNOTs
# already follow the line. A chain 0→1→2→3 needs no SWAP and uses the minimum of 3 CNOTs.
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

# The device: a line 0 - 1 - 2 - 3, and the only gates it runs.
coupling_map = CouplingMap.from_line(4)
basis_gates = ["rz", "sx", "x", "cx"]

# Hadamard on qubit 0 gives (|0⟩ + |1⟩)/√2; each CNOT then copies the 1 branch onto the next neighbor.
# Starting every CNOT at qubit 0 would force SWAPs, because qubit 0 has a single neighbor.
ghz = QuantumCircuit(4)
ghz.h(0)
ghz.cx(0, 1)
ghz.cx(1, 2)
ghz.cx(2, 3)

# Mapping to the basis and the coupling map rewrites h as rz, sx, rz and inserts nothing else.
qc = transpile(ghz, coupling_map=coupling_map, basis_gates=basis_gates, optimization_level=1, seed_transpiler=7)

# The number of cx and the depth are the cost on hardware.
print(qc.count_ops(), "depth", qc.depth())
