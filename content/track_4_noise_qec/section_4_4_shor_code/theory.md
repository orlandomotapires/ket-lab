## An error that is neither X nor Z

A real qubit does not suffer clean bit flips or clean phase flips. Something small drifts it by a rotation such as $R_x(0.6)$, which is neither $X$ nor $Z$, and the bit-flip and phase-flip codes each handle only one of the two. Shor's nine-qubit code handles every error on a single qubit, and it does so by stacking the two codes, a step called **concatenation**: the qubit is first encoded in the phase-flip code, and each of the three qubits of that code is then encoded in the bit-flip code.

$$
|0\rangle \to |0_L\rangle = \frac{(|000\rangle + |111\rangle)^{\otimes 3}}{2\sqrt2}, \qquad
|1\rangle \to |1_L\rangle = \frac{(|000\rangle - |111\rangle)^{\otimes 3}}{2\sqrt2} .
$$

The nine qubits form three blocks, $(0,1,2)$, $(3,4,5)$ and $(6,7,8)$, and the first qubit of each block is its leader. The encoding takes two steps. Two CNOT gates from qubit 0 to qubits 3 and 6 and a Hadamard on each leader give $\alpha|{+}{+}{+}\rangle + \beta|{-}{-}{-}\rangle$ on the leaders. Then two CNOT gates from each leader fill its block, turning $|0\rangle$ into $|000\rangle$ and $|1\rangle$ into $|111\rangle$, so that a leader in $|\pm\rangle$ becomes $(|000\rangle \pm |111\rangle)/\sqrt2$. The platform follows Qiskit and writes qubit 0 on the right of a ket; Nielsen & Chuang write it on the left.

## Following a Y error through the decoder

The circuit has no ancillas. Decoding is the encoding run backwards, with a Toffoli gate as the majority vote: in a block $(a,b,c)$, after $\mathrm{CNOT}(a,b)$ and $\mathrm{CNOT}(a,c)$ the qubits $b$ and $c$ hold the block's syndrome, and $\mathrm{Toffoli}(b,c,a)$ flips the leader $a$ exactly when $a$ was the flipped qubit. The same three gates in the Hadamard basis, on the leaders, vote on the phase.

Put a $Y$ error on qubit 4, in the second block. Since $Y=iXZ$, it is a bit flip together with a phase flip.

The $X_4$ part flips qubit 4 only. After the two CNOT gates of block 2, qubit 4 holds the syndrome bit 1 and qubit 5 holds 0, so the Toffoli does not fire and the leader keeps its value. The bit flip is gone.

The $Z_4$ part is a different matter. A $Z$ on the target of a CNOT propagates to the control, so after the CNOT gates it also sits on the leader, qubit 3. A phase flip anywhere in a block ends up as a phase flip of the whole block, which turns $|000\rangle+|111\rangle$ into $|000\rangle-|111\rangle$ and back. The blocks are the three qubits of a phase-flip code, so the Hadamards and the second vote on the leaders find block 2 and fix it. Qubit 0 holds $|\psi\rangle$ again.

## Why every error on one qubit is covered

An error on one qubit is a $2\times2$ operator $E = e_0 I + e_1 X + e_2 Y + e_3 Z$, because $I$, $X$, $Y$, $Z$ span the $2\times2$ matrices. The code corrects each of the four on any qubit, so by linearity it corrects $E$. The syndrome measurement projects the error onto one of the four Pauli terms and the recovery undoes that one: a continuum of errors is corrected by correcting a finite set, which is the **discretization of errors**. The validator tests this with the rotation $R_z(0.9)\,R_x(0.6)\,R_y(1.3)$ on qubit 4. After the decoding, qubit 0 holds $|\psi\rangle$ exactly, and the other qubits hold the syndrome, entangled with the error.

The stabilizers are $Z_0Z_1$, $Z_1Z_2$ and the same pairs in the other two blocks, which detect bit flips, and $X_0X_1X_2X_3X_4X_5$ and $X_3X_4X_5X_6X_7X_8$, which detect phase flips of whole blocks.

## Two errors: some survive, most do not

Not every pair of errors is a disaster, and the pairs that are corrected surprise people. $X$ on qubit 0 and $Z$ on qubit 3 are both removed, the first inside block 1 and the second by the outer vote. $Z$ on qubits 0 and 1 cancel inside block 1, because $Z_0Z_1$ is a stabilizer and acts as the identity on the code.

Two of the failures are worth working out. $X$ on qubits 0 and 1, in the same block, has the syndrome of $X$ on qubit 2, so the inner vote flips qubit 2 as well. What is left is $X\otimes X\otimes X$ on the block, which acts as $+1$ on $|0_L\rangle$ and $-1$ on $|1_L\rangle$: a logical $Z$. $Z$ on qubits 0 and 3, in different blocks, gives two block phase flips, which look like a flip of the third block. The outer vote adds a third $Z$, one per block, and $|0_L\rangle$ and $|1_L\rangle$ are exchanged: a logical $X$.

Out of the $36\times 9 = 324$ ways to put an error on two different qubits (36 pairs of qubits, 9 pairs of Paulis), 144 fail. Lesson 4.8 counts them.

## In the lab

There is no button for $Z$ on qubits 0 and 1. Predict what the decoder does with it, and then compare your guess with the buttons "Z on 0 and 3" and "X on 0, Z on 3", which you can run.
