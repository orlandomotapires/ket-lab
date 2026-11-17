## The control changes, the target does not

Take a CNOT whose control is in $|+\rangle$ and whose target is in $|-\rangle = (|0\rangle - |1\rangle)/\sqrt{2}$. A CNOT applies $X$ to the target when the control is 1, so you expect the target to change. It does not. The target stays in $|-\rangle$, and the control goes from $|+\rangle$ to $|-\rangle$.

The reason is that $|-\rangle$ is an **eigenstate** of $X$: the gate returns the same state multiplied by a number, called the **eigenvalue**.

$$
X|-\rangle = \frac{|1\rangle - |0\rangle}{\sqrt{2}} = -|-\rangle
$$

For a general gate $U$ the eigenvalue is a phase $e^{i\varphi}$, and $U|\psi\rangle = e^{i\varphi}|\psi\rangle$. On a single qubit that factor is a global phase and nobody can measure it.

Controlled by another qubit, the same factor becomes visible. Write the control first, as in a textbook (Qiskit's labels put qubit 0 on the right). If the control is the basis state $|x\rangle$, then $X$ acts on the target $x$ times and each time multiplies by $-1$:

$$
\text{CNOT}\,|x\rangle|-\rangle = (-1)^x\,|x\rangle|-\rangle
$$

By linearity, a control in $|+\rangle$ gives

$$
\text{CNOT}\,|+\rangle|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}\,|-\rangle = |-\rangle|-\rangle
$$

The sign sits in the term where the control is $|1\rangle$, so it is a relative phase of the control. The output is still a product state, with no entanglement.

## Phase kickback

This effect is called **phase kickback**. It holds for any controlled-$U$ whose target is an eigenstate of $U$ with eigenvalue $e^{i\varphi}$:

$$
\text{controlled-}U\,\big(\alpha|0\rangle + \beta|1\rangle\big)|\psi\rangle = \big(\alpha|0\rangle + e^{i\varphi}\beta|1\rangle\big)|\psi\rangle
$$

It is easy to look at the target, because that is where the gate points, and conclude that nothing happened. The change is on the other qubit. If the target were $|0\rangle$ or $|1\rangle$, which are not eigenstates of $X$, the CNOT would entangle the two qubits instead.

Deutsch's algorithm and its relatives put the auxiliary qubit in $|-\rangle$ so that an oracle writes $(-1)^{f(x)}$ on the input. Phase estimation (lesson 2.8) does the same with an arbitrary $U$.

## In the lab

Before you run anything, replace the target by $|+\rangle$, which is an eigenstate of $X$ with eigenvalue $+1$. Predict what happens to the control, then check it.
