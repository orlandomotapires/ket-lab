## Eigenstates

A state $|\psi\rangle$ is an **eigenstate** of a gate $U$ when the gate only multiplies it by a phase:

$$
U|\psi\rangle = e^{i\varphi}|\psi\rangle
$$

The factor $e^{i\varphi}$ is the **eigenvalue**. The state $|-\rangle$ is an eigenstate of $X$ with eigenvalue $-1$:

$$
X|-\rangle = \frac{|1\rangle - |0\rangle}{\sqrt{2}} = -|-\rangle
$$

For a single qubit this sign is a global phase and cannot be measured.

## The CNOT acting on $|-\rangle$

Write the control qubit first. With the target in $|-\rangle$, the CNOT applies $X$ to the target when the control is $|1\rangle$, and each application multiplies the state by $-1$:

$$
\text{CNOT}\,|x\rangle|-\rangle = (-1)^x\,|x\rangle|-\rangle
$$

The target is unchanged and the sign has moved to the control's term. If the control is in superposition, the sign is a relative phase:

$$
\text{CNOT}\,|+\rangle|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}\,|-\rangle = |-\rangle|-\rangle
$$

## Phase kickback

The gate acts on the target, yet the control changes. This is **phase kickback**. It holds for any controlled-$U$: if the target is an eigenstate of $U$ with eigenvalue $e^{i\varphi}$, then

$$
\text{controlled-}U\,\big(\alpha|0\rangle + \beta|1\rangle\big)|\psi\rangle = \big(\alpha|0\rangle + e^{i\varphi}\beta|1\rangle\big)|\psi\rangle
$$

The phase $e^{i\varphi}$ is applied to the $|1\rangle$ term of the control.

Deutsch, Deutsch–Jozsa and Bernstein–Vazirani use an auxiliary qubit in $|-\rangle$ so that the oracle writes $(-1)^{f(x)}$ on the input. Phase estimation uses the same effect with an arbitrary $U$.

## In the lab

On the Bloch spheres, the control's vector goes from $+x$ to $-x$ at the CNOT, and the target's vector does not move. If the target were $|0\rangle$ or $|1\rangle$ instead, the CNOT would entangle the two qubits, as in the Bell states lesson.
