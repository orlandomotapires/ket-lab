## Two codes, one after the other

The bit-flip code corrects $X$ but not $Z$, and the phase-flip code corrects $Z$ but not $X$. A general error on one qubit is neither. The nine-qubit **Shor code** encodes one logical qubit so that any error on a single qubit is corrected. It **concatenates** the two codes: the qubit is first encoded in the phase-flip code, and each of its three qubits is then encoded in the bit-flip code.

$$
|0\rangle \to |0_L\rangle = \frac{(|000\rangle + |111\rangle)^{\otimes 3}}{2\sqrt2}, \qquad
|1\rangle \to |1_L\rangle = \frac{(|000\rangle - |111\rangle)^{\otimes 3}}{2\sqrt2}
$$

The nine qubits form three blocks, $(0,1,2)$, $(3,4,5)$ and $(6,7,8)$. The first qubit of each block is its leader. The circuit is:

1. Two CNOT gates from qubit 0 to qubits 3 and 6, and a Hadamard gate on each leader: $|\psi\rangle \to \alpha|{+}{+}{+}\rangle + \beta|{-}{-}{-}\rangle$ on the leaders.
2. In each block, two CNOT gates from the leader: $|0\rangle \to |000\rangle$, $|1\rangle \to |111\rangle$ (the leader $|+\rangle$ becomes $(|000\rangle + |111\rangle)/\sqrt2$, and $|-\rangle$ becomes $(|000\rangle - |111\rangle)/\sqrt2$).

Qubit ordering: the platform labels basis states with qubit 0 on the right, as in Qiskit. Nielsen & Chuang write qubit 0 on the left.

## How the code corrects

A bit flip $X$ on a qubit of a block exchanges $|000\rangle \leftrightarrow |100\rangle$ and so on within that block, and the block's parities identify the qubit (the bit-flip syndrome). A phase flip $Z$ on any qubit of a block changes the sign between $|000\rangle$ and $|111\rangle$ in that block: $Z$ turns $|000\rangle + |111\rangle$ into $|000\rangle - |111\rangle$ and the other way round, which is a phase flip of the block as a whole. The three blocks are the three qubits of a phase-flip code, so comparing the signs of the blocks identifies the block and corrects it.

The stabilizers are $Z_0Z_1,\ Z_1Z_2$ (and the same in the other two blocks), which detect bit flips, and $X_0X_1X_2X_3X_4X_5,\ X_3X_4X_5X_6X_7X_8$, which detect block phase flips. Here $Z_iZ_j$ means $Z$ on qubits $i$ and $j$.

The circuit here does not use ancillas. Decoding is the encoding run backwards, with a Toffoli gate that takes the majority vote. In a block $(a,b,c)$, after $\mathrm{CNOT}(a,b)$ and $\mathrm{CNOT}(a,c)$ the qubits $b$ and $c$ hold the syndrome, and $\mathrm{Toffoli}(b,c,a)$ flips the leader $a$ exactly when $a$ was the flipped qubit. The same three gates in the Hadamard basis, on the leaders, vote on the phase.

## Discretization of errors

Any error on one qubit acts as a $2\times2$ operator $E = e_0 I + e_1 X + e_2 Y + e_3 Z$, since $I, X, Y, Z$ span the $2\times 2$ matrices. The code corrects each of $I, X, Y, Z$ on any qubit, because $Y = iXZ$ is a bit flip together with a phase flip, and both are corrected. By linearity, the recovery corrects $E$ too. The syndrome measurement projects the error onto one of the four Pauli terms, and the recovery undoes that one. This is the **discretization of errors**: a continuum of errors is corrected by correcting a finite set.

The control "Arbitrary rotation" injects $R_z(0.9)\,R_x(0.6)\,R_y(1.3)$ on qubit 4. After the decoding, qubit 0 holds $|\psi\rangle$ exactly, and the remaining qubits hold the syndrome information, entangled with the error.

## What the code does not correct

Some errors on two qubits are corrected and others are not. $X$ on qubit 0 and $Z$ on qubit 3 are corrected, since the bit flip is removed inside block 1 and the phase flip in block 2 by the outer code. Two errors of the same kind can fail:

- $Z$ on qubits 0 and 3 (different blocks) gives two block phase flips. The outer code treats them as a flip of the third block, and the result is $Z$ on one qubit of each block, which exchanges $|0_L\rangle$ and $|1_L\rangle$: a logical $X$.
- $X$ on qubits 0 and 1 (same block) has the syndrome of $X$ on qubit 2, so the inner majority vote flips qubit 2 as well. What remains is $X\otimes X\otimes X$ on the block, which acts as $+1$ on $|0_L\rangle$ and $-1$ on $|1_L\rangle$: a logical $Z$.

## In the lab

- The buttons choose the injected error. Try the single-qubit errors, then those on two qubits.
- Bloch spheres: the state of each qubit after the decoding. Qubit 0 is $|\psi\rangle$.
- Histogram: the register shows the leaders 0, 3 and 6.
