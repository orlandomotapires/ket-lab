## One CNOT that costs four

Take three qubits on a line, 0 - 1 - 2, and a circuit with a single `cx(0, 2)`. The device cannot run it: qubits 0 and 2 are not neighbors. The transpiler moves the state of qubit 0 next to qubit 2 with a SWAP, runs the CNOT, and the circuit that reaches the device has four CNOTs instead of one. A SWAP is three CNOTs,

$$
\mathrm{SWAP} = \mathrm{CNOT}_{01}\,\mathrm{CNOT}_{10}\,\mathrm{CNOT}_{01},
$$

so one gate of distance two costs $3 + 1 = 4$. Transpilation is this kind of rewriting: it takes the circuit you wrote and produces one that uses only what the device offers, and that prepares the same state up to a global phase.

## What the device offers

Two things are fixed by the hardware. The first is the set of **basis gates**, the only gates it runs; on IBM devices that is something like $\{R_z, \sqrt X, X, \mathrm{CNOT}\}$ (or ECR instead of CNOT), with $\sqrt X$ written `sx`. A Hadamard gate is not in it, so `h` becomes three native gates:

$$
H = e^{i\pi/4}\, R_z(\pi/2)\,\sqrt X\, R_z(\pi/2).
$$

That is possible because any single-qubit gate is a product of rotations, and single-qubit gates with CNOT are universal (Nielsen & Chuang, §4.5). The factor $e^{i\pi/4}$ is a global phase and is dropped. The $R_z$ gates are done in software, by shifting the phase of the pulses that follow, so they cost almost nothing; the two-qubit gate is the slow and noisy one.

The second is the **coupling map**, the list of pairs of physical qubits that can run a two-qubit gate. `CouplingMap.from_line(4)` is the line 0 - 1 - 2 - 3. Real devices have more links than a line, never all of them.

## Choosing where things go

The transpiler makes two choices that change the cost. The **layout** says which physical qubit holds each logical qubit, and a good one puts qubits that interact next to each other. The **routing** decides where the SWAPs go. The argument `optimization_level` (0 to 3) sets how hard it works on both, and since the search is randomized, `seed_transpiler` makes a run repeatable.

To compare two versions of a circuit, count the two-qubit gates (`qc.count_ops()`): a two-qubit gate typically has an error rate ten times that of a single-qubit gate or more. The `qc.depth()` counts layers of gates that run in parallel, and matters because a longer circuit leaves the qubits waiting and they decohere (lesson 5.3).

## A GHZ state on a line

The usual GHZ circuit is an $H$ on qubit 0 followed by $\mathrm{CNOT}_{0\to1}$, $\mathrm{CNOT}_{0\to2}$, $\mathrm{CNOT}_{0\to3}$. On the line 0 - 1 - 2 - 3, qubit 0 has one neighbor. In the code of this lesson the transpiler ends with 9 CNOTs at level 0, 6 at level 1 and 4 at levels 2 and 3, and none of these is the minimum.

Rewrite the circuit instead: $\mathrm{CNOT}_{0\to1}$, then $\mathrm{CNOT}_{1\to2}$, then $\mathrm{CNOT}_{2\to3}$ prepares the same state, needs no SWAP, and has 3 CNOTs, the least that four connected qubits allow. The transpiler improves a circuit but keeps its structure, so a circuit written without the device in mind starts at a disadvantage.

A count key in Qiskit puts qubit 0 last: a circuit that only flips qubit 0 returns `'0001'` on four qubits.
