## A phase flip is a bit flip in another basis

The three-qubit bit-flip code does not detect a phase flip $Z$. The Hadamard gate exchanges the two kinds of error: $HXH = Z$ and $HZH = X$. Applying $H$ to every qubit of the bit-flip code gives a code that corrects phase flips.

Recall that $H|0\rangle = |+\rangle$ and $H|1\rangle = |-\rangle$, with $|\pm\rangle = (|0\rangle \pm |1\rangle)/\sqrt2$. Since $Z|+\rangle = |-\rangle$ and $Z|-\rangle = |+\rangle$, a phase flip exchanges $|+\rangle$ and $|-\rangle$, just as a bit flip exchanges $|0\rangle$ and $|1\rangle$.

## Encoding

The **three-qubit phase-flip code** encodes

$$
\alpha|0\rangle + \beta|1\rangle \;\longrightarrow\; \alpha|{+}{+}{+}\rangle + \beta|{-}{-}{-}\rangle
$$

with the bit-flip encoding (two CNOT gates) followed by a Hadamard gate on each of the three qubits. The code states are $|0_L\rangle = |{+}{+}{+}\rangle$ and $|1_L\rangle = |{-}{-}{-}\rangle$.

## Syndrome measurement

A phase flip on qubit 1 gives $\alpha|{+}{-}{+}\rangle + \beta|{-}{+}{-}\rangle$. The operators $X_0X_1$ and $X_1X_2$ have the same eigenvalue on both terms, so measuring them reveals nothing about $\alpha$ and $\beta$. They are the **stabilizers** of the code: both code states are eigenstates with eigenvalue $+1$ of $X_0X_1$ and $X_1X_2$. A phase flip changes the eigenvalues of the stabilizers that act with $X$ on the flipped qubit:

| $X_0X_1$ | $X_1X_2$ | Syndrome | Error | Correction |
| :-- | :-- | :-- | :-- | :-- |
| $+1$ | $+1$ | 00 | none | none |
| $-1$ | $+1$ | 10 | $Z$ on qubit 0 | $Z$ on qubit 0 |
| $-1$ | $-1$ | 11 | $Z$ on qubit 1 | $Z$ on qubit 1 |
| $+1$ | $-1$ | 01 | $Z$ on qubit 2 | $Z$ on qubit 2 |

A stabilizer $X\otimes X$ is measured by conjugating a parity check with Hadamard gates: $H^{\otimes 2}$, two CNOT gates onto an ancilla (which compute the parity $Z\otimes Z$ in the rotated basis), and $H^{\otimes 2}$ again. Doing the basis change once on all three data qubits, the circuit is:

1. Apply $H$ to each data qubit. The phase flip is now a bit flip.
2. Compute the two parities onto ancillas 3 and 4 with CNOT gates.
3. Apply a Toffoli gate controlled by the ancillas to the qubit the syndrome points to (deferred measurement), as for the bit-flip code.
4. Apply $H$ to each data qubit again, which returns the state to the code space.

Qubit ordering: ancilla bits are written $a_3a_4$, with $a_3$ on qubit 3. The platform labels basis states with qubit 0 on the right, as in Qiskit.

## What the code does not correct

- Two phase flips give the syndrome of a single flip on the third qubit, and the "correction" produces $Z^{\otimes 3}$, a logical $X$.
- A bit flip $X$ on any qubit does not change the stabilizer eigenvalues (the stabilizers commute with $X$), so the syndrome is 00. On the code states, $X_0$ maps $\alpha|{+}{+}{+}\rangle + \beta|{-}{-}{-}\rangle$ to $\alpha|{+}{+}{+}\rangle - \beta|{-}{-}{-}\rangle$, a logical $Z$ that is not detected.

Each of the two codes protects against one kind of error. The next lesson combines them.

## In the lab

- The buttons choose the injected error. Compare $Z$ on one qubit, $Z$ on two qubits and $X$ on qubit 0.
- Register: with the cursor after the syndrome, the ancilla bits appear.
- Bloch spheres: the state of each data qubit. The qubits are entangled, so each one alone is a mixed state.
