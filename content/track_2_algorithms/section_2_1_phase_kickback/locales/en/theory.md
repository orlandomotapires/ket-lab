## Eigenstates

A state is an **eigenstate** of a gate when the gate does not change it, except by a factor:

$$
U|\psi\rangle = e^{i\varphi}|\psi\rangle
$$

The factor $e^{i\varphi}$ is the **eigenvalue**. The state $|-\rangle$ is an eigenstate of the $X$ gate, with eigenvalue $-1$:

$$
X|-\rangle = \frac{|1\rangle - |0\rangle}{\sqrt{2}} = -|-\rangle
$$

On its own, this sign is a global phase and changes nothing that can be measured.

## The CNOT seen from another angle

Writing the control on the left, for clarity: with the target in $|-\rangle$, the CNOT applies $X$ to the target only when the control is $1$, and each application produces the sign $-1$:

$$
\text{CNOT}\,|x\rangle|-\rangle = (-1)^x\,|x\rangle|-\rangle
$$

The target stays in $|-\rangle$. The sign ended up on the control's term. If the control is in superposition, the sign is no longer global and becomes a relative phase:

$$
\text{CNOT}\,|+\rangle|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}\,|-\rangle = |-\rangle|-\rangle
$$

## Phase kickback

The gate acts "on the target", but it is the control that changes. This effect is called **phase kickback** and holds for any controlled gate: if the target is an eigenstate of $U$ with eigenvalue $e^{i\varphi}$, the phase $e^{i\varphi}$ goes back to the $|1\rangle$ term of the control.

## Why this matters

It is the mechanism behind almost every algorithm in this track. Deutsch-Jozsa and Bernstein-Vazirani use an auxiliary qubit in $|-\rangle$ to turn a function's answer into a phase. Phase estimation uses the same trick with an arbitrary gate, and Shor's algorithm is built on top of it.

## In the lab

On the Bloch spheres, the control's vector jumps from $+x$ to $-x$ at the CNOT step, while the target's stays still. Compare with what happens if the target is in $|0\rangle$ or $|1\rangle$: then the CNOT entangles the qubits, as in the Bell states lesson.
