## From circuit to device

A circuit written with H, T, Toffoli or any other gate cannot run as it is. A quantum processor executes a small set of **native gates**, the **basis gates**, and applies two-qubit gates only to certain pairs of qubits. **Transpilation** rewrites the circuit so that it uses only those gates and those pairs. The rewritten circuit prepares the same state, up to a global phase.

Two ideas from the universality results (Nielsen & Chuang, §4.5) make this possible: any single-qubit gate is a product of rotations, and single-qubit gates with CNOT are universal.

## Basis gates

IBM devices use a basis such as $\{R_z, \sqrt X, X, \mathrm{CNOT}\}$ or $\{R_z, \sqrt X, X, \mathrm{ECR}\}$, where $\sqrt X$ is the gate `sx`. The Hadamard gate is not native. It is rewritten as

$$
H = e^{i\pi/4}\, R_z(\pi/2)\,\sqrt X\, R_z(\pi/2)
$$

so one `h` becomes three native gates (the factor $e^{i\pi/4}$ is a global phase). The $R_z$ gates are implemented in software by shifting the phase of later pulses, so they cost almost nothing. The two-qubit gate is the slow and noisy one.

## Coupling map

The **coupling map** lists which pairs of physical qubits can run a two-qubit gate. `CouplingMap.from_line(4)` is the line 0 - 1 - 2 - 3. Real devices have more connections, but never all pairs.

If the circuit asks for a CNOT on qubits that are not neighbors, the transpiler inserts **SWAP** gates to move the quantum state until the two qubits are adjacent. A SWAP is three CNOTs:

$$
\mathrm{SWAP} = \mathrm{CNOT}_{01}\,\mathrm{CNOT}_{10}\,\mathrm{CNOT}_{01}
$$

A CNOT between qubits two steps apart therefore costs $3 + 1 = 4$ CNOTs on a line.

## Layout, depth and cost

Transpilation has two choices that change the cost.

- **Layout**: which physical qubit holds each logical qubit. A good initial layout puts qubits that interact next to each other.
- **Routing**: where the SWAPs go.

`optimization_level` (0 to 3) controls how much effort the transpiler spends on both. Higher levels find fewer SWAPs and merge neighboring single-qubit gates. The search is randomized, so `seed_transpiler` makes the result repeatable.

Two numbers measure the cost of the result:

- the **number of two-qubit gates** (`qc.count_ops()`), since a two-qubit gate typically has an error rate ten times or more that of a single-qubit gate;
- the **depth** (`qc.depth()`), the number of layers of gates that run in parallel, since a deeper circuit takes longer and the qubits decohere meanwhile (lesson 5.3).

## GHZ on a line

The GHZ circuit with $\mathrm{CNOT}_{0\to1}$, $\mathrm{CNOT}_{0\to2}$, $\mathrm{CNOT}_{0\to3}$ needs qubit 0 to interact with all the others. On a line, qubit 0 has one neighbor, so SWAPs are unavoidable: the transpiler gives 6 CNOTs at level 1 and 4 at level 3. The chain $\mathrm{CNOT}_{0\to1}$, $\mathrm{CNOT}_{1\to2}$, $\mathrm{CNOT}_{2\to3}$ prepares the same state with 3 CNOTs, the minimum for 4 qubits, and needs no SWAP.

The transpiler improves a circuit but does not change its structure. Writing the logical circuit with the device in mind is part of the work.

The platform shows the transpiled circuit in `qc`, with gates `rz`, `sx` and `cx` instead of `h`. Qubit 0 is the rightmost label, as in Qiskit.
