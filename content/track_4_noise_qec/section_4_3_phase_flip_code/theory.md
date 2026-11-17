## A phase flip is a bit flip in another basis

Take the three-qubit state $|{+}{+}{+}\rangle$ and apply $Z$ to the middle qubit. You get $|{+}{-}{+}\rangle$. That looks exactly like what $X$ does to $|000\rangle$ when it hits the middle qubit: it exchanges the two basis states of that qubit. The reason is that $Z|+\rangle = |-\rangle$ and $Z|-\rangle = |+\rangle$, with $|\pm\rangle = (|0\rangle \pm |1\rangle)/\sqrt2$. In the $|\pm\rangle$ basis, $Z$ plays the part of $X$.

The Hadamard gate changes between the two bases: $H|0\rangle=|+\rangle$, $H|1\rangle=|-\rangle$, $HXH=Z$ and $HZH=X$. So the bit-flip code, written in the Hadamard basis, protects against phase flips. The **three-qubit phase-flip code** is the bit-flip encoding (two CNOT gates) followed by a Hadamard gate on each qubit:

$$
\alpha|0\rangle + \beta|1\rangle \;\longrightarrow\; \alpha|{+}{+}{+}\rangle + \beta|{-}{-}{-}\rangle ,
$$

with code states $|0_L\rangle = |{+}{+}{+}\rangle$ and $|1_L\rangle = |{-}{-}{-}\rangle$.

## What the syndrome measures

In lesson 4.2 the parities were $Z_0Z_1$ and $Z_1Z_2$. Here the same questions are asked in the Hadamard basis, so the operators are $X_0X_1$ and $X_1X_2$. Both code states are eigenstates of both operators with eigenvalue $+1$, which is why measuring them says nothing about $\alpha$ and $\beta$. They are the **stabilizers** of the code: the operators that leave every code state unchanged. (Lesson 4.5 develops this idea fully.)

Work through $Z$ on qubit 1, which gives $\alpha|{+}{-}{+}\rangle + \beta|{-}{+}{-}\rangle$. Since $X|\pm\rangle=\pm|\pm\rangle$, $X_0X_1$ has eigenvalue $(+1)(-1)=-1$ on the first term and $(-1)(+1)=-1$ on the second. $X_1X_2$ gives $-1$ on both terms as well. Both stabilizers read $-1$, the syndrome is 11, and that pattern belongs to qubit 1, as in lesson 4.2. A flip on qubit 0 turns only $X_0X_1$ to $-1$ (syndrome 10), and a flip on qubit 2 only $X_1X_2$ (syndrome 01).

## The circuit

Measuring $X\otimes X$ means conjugating a parity check with Hadamard gates on both qubits. Doing the basis change once on all three data qubits serves both checks:

1. Apply $H$ to each data qubit. The phase flip is now a bit flip.
2. Compute the two parities onto ancillas 3 and 4 with CNOT gates.
3. Apply Toffoli gates controlled by the ancillas to the qubit the syndrome points to, as in 4.2.
4. Apply $H$ to each data qubit again, to return to the code space.

The ancilla bits are written $a_3a_4$ with $a_3$ on qubit 3; the platform prints basis states with qubit 0 on the right, as Qiskit does.

## The mirror image of 4.2

Everything that went wrong for the bit-flip code goes wrong here with the roles reversed. Two phase flips have the syndrome of a single flip on the third qubit, and the "correction" completes $Z^{\otimes 3}$, which exchanges $|0_L\rangle=|{+}{+}{+}\rangle$ and $|1_L\rangle=|{-}{-}{-}\rangle$: a logical $X$. And $X$ errors are invisible. $X$ commutes with $X_0X_1$ and $X_1X_2$, so the syndrome is 00, but $X_0$ takes $\alpha|{+}{+}{+}\rangle+\beta|{-}{-}{-}\rangle$ to $\alpha|{+}{+}{+}\rangle-\beta|{-}{-}{-}\rangle$, because $X|{-}\rangle=-|{-}\rangle$. That is a logical $Z$, and nothing signals it.

Each code covers one kind of error, and an error like $Y=iXZ$ needs both. The next lesson combines them.

## In the lab

Predict the final state for the buttons "Z on 0 and 1" and "X on 0" before pressing them. The qubits are entangled, so a single data qubit on the Bloch sphere is a mixed state, and the fidelity of the whole code state is what tells you whether the recovery worked.
