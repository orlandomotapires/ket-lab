## Controlled gates

A controlled gate applies an operation to the **target** only when the **control** is $1$. $CS$ applies $S$ to the target, which amounts to multiplying the amplitude of $|11\rangle$ by $i$:

$$
CS = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & i \end{pmatrix}
$$

The phase sits on a basis state of **two** qubits. With basis inputs such as $|01\rangle$ or $|10\rangle$ nothing changes, and for $|11\rangle$ only a global phase shows up; that is why the validator uses superpositions, where the relative phase becomes an observable difference.

## How the solution works

The trick is to change what the gate sees. If $a$ and $b$ are the values of the two qubits, after `qc.cx(0, 1)` qubit 1 holds $a \oplus b$ (the parity). Each $T$ adds $\pi/4$ per qubit in $1$; the $T^{\dagger}$ on the parity subtracts $\pi/4$. The total phase is

$$
\frac{\pi}{4}\bigl(a + b - (a \oplus b)\bigr) = \frac{\pi}{4}\cdot 2ab = \frac{\pi}{2}\,ab
$$

which is $\pi/2$ only for $a = b = 1$: exactly $CS$.

## Useful identities

- $S = T^2$ and $Z = S^2 = T^4$: phase gates whose angles add up.
- $HZH = X$ and $HXH = Z$: the Hadamard swaps the $X$ and $Z$ axes.
- $CZ = H_{\text{target}}\,\text{CNOT}\,H_{\text{target}}$: a Hadamard on the target before and after the CNOT gives the CZ. In Qiskit, `qc.h(1); qc.cx(0, 1); qc.h(1)`.
- Hadamard on both qubits before and after a CNOT reverses their roles: you get a CNOT from 1 to 0.
- $\text{SWAP}$ = three CNOTs: `qc.cx(0, 1); qc.cx(1, 0); qc.cx(0, 1)`.

## Universality

The CNOT and single-qubit gates form a **universal set**: with them you can build any multi-qubit gate, as accurately as you wish. Decomposing operations into CNOTs and simple gates, as here, is what real machines do to run a circuit.

## Controlled Rz versus CS

In lesson 1.3 we saw that $R_z(\theta)$ and $P(\theta)$ differ only by a global phase. When the gate is **controlled**, that phase stops being global: it becomes a relative phase and the gate also acts on the control qubit. That is why $CS$ is not the same as a controlled $R_z$.
