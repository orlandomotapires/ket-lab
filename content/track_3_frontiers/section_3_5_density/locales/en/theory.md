## When we do not know the state

So far, the qubit was always in a well-defined state $|\psi\rangle$: a **pure state**. On a real computer, noise acts at random: sometimes a gate fails, sometimes it does not. After that, all we know is that the qubit is in $|\psi_1\rangle$ with probability $p_1$, in $|\psi_2\rangle$ with probability $p_2$, and so on. This is a **mixed state**.

A mixed state is not a superposition. The superposition $\frac{|0\rangle + |1\rangle}{\sqrt2}$ is a pure state, with a well-defined phase; a coin that gives $|0\rangle$ or $|1\rangle$ with 50% each has no phase at all.

## The density matrix

Both cases fit in the same description, the **density matrix**:

$$
\rho = \sum_i p_i\, |\psi_i\rangle\langle\psi_i|
$$

- The diagonal gives the measurement probabilities: $P(0) = \rho_{00}$ and $P(1) = \rho_{11}$.
- The **purity** $\mathrm{Tr}(\rho^2)$ is $1$ for a pure state and less than $1$ for a mixed one; for 1 qubit, the minimum is $1/2$.
- On the Bloch sphere, pure states sit on the surface and mixed states sit inside, with a shortened vector.

The entangled qubits of Track 1 shrank on the sphere for the same reason: the state of one qubit of a Bell pair, looked at alone, is mixed. It is obtained by the **partial trace**, which discards the other qubit.

## Noise channels

A noisy operation acts on $\rho$ through **Kraus operators** $K_k$:

$$
\rho \;\longrightarrow\; \sum_k K_k\, \rho\, K_k^\dagger, \qquad \sum_k K_k^\dagger K_k = I
$$

An error that applies $X$ with probability $p_x$, $Z$ with $p_z$ and nothing otherwise has $K_0 = \sqrt{1-p_x-p_z}\,I$, $K_1 = \sqrt{p_x}\,X$ and $K_2 = \sqrt{p_z}\,Z$. The most common channels have names: *bit flip*, *phase flip*, depolarizing, amplitude damping.

## An error is not the same as a wrong answer

The probability that **an error happens** is not the probability that **the answer comes out wrong**. The effect of an error depends on where it occurs and on what comes after: a $Z$ followed by a Hadamard becomes a full $X$, while an $X$ between $T$ and $T^\dagger$ becomes a rotation that only sometimes changes the result. That is why error correction, in the next lesson, looks at the type of error and not only at its frequency.

## In the lab

The `default.mixed` device simulates the density matrix. In the **Bloch spheres** tab, watch the vector shrink at the error step; the panel shows the purity of the state. The **Register** tab shows $P(0)$ and $P(1)$.
