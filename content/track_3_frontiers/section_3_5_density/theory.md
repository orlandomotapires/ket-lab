## Pure and mixed states

A **pure state** is a single state vector $|\psi\rangle$. When noise acts at random, for example a gate that fails with some probability, we only know that the qubit is in $|\psi_i\rangle$ with probability $p_i$. This is a **mixed state**.

A mixed state is not a superposition. $(|0\rangle+|1\rangle)/\sqrt2$ is a pure state with a definite relative phase. A coin that yields $|0\rangle$ or $|1\rangle$ with probability 1/2 each has no phase to speak of, and its measurements in the $X$ basis are random.

## The density operator

Both cases are described by the **density operator** (density matrix)

$$
\rho = \sum_i p_i\, |\psi_i\rangle\langle\psi_i|
$$

which is Hermitian, positive semidefinite and has $\mathrm{Tr}\,\rho = 1$.

- In the computational basis, the diagonal gives the measurement probabilities: $P(0)=\rho_{00}$, $P(1)=\rho_{11}$.
- The **purity** $\mathrm{Tr}(\rho^2)$ equals 1 for a pure state and is less than 1 for a mixed state. For one qubit its minimum is $1/2$ (for $d$ dimensions, $1/d$).
- On the Bloch sphere, pure states lie on the surface and mixed states inside it. The Bloch vector has length $\sqrt{2\,\mathrm{Tr}(\rho^2)-1}$.

One qubit of an entangled pair is also mixed. Its state is the **reduced density operator**, obtained by the partial trace over the other qubit. This is why the Bloch vectors of entangled qubits in Track 1 were shorter than 1.

## Quantum channels

A noisy operation takes $\rho$ to

$$
\rho \;\longrightarrow\; \sum_k K_k\, \rho\, K_k^\dagger, \qquad \sum_k K_k^\dagger K_k = I
$$

where the $K_k$ are the **Kraus operators** (operator-sum representation). The completeness condition keeps $\mathrm{Tr}\,\rho = 1$. An error that applies $X$ with probability $p_x$, $Z$ with probability $p_z$ and nothing otherwise has

$$
K_0 = \sqrt{1-p_x-p_z}\,I, \qquad K_1 = \sqrt{p_x}\,X, \qquad K_2 = \sqrt{p_z}\,Z
$$

and $\sum_k K_k^\dagger K_k = (1-p_x-p_z)I + p_xI + p_zI = I$. Standard single-qubit channels are the bit flip, phase flip, depolarizing and amplitude damping channels. The first two are the cases $p_z=0$ and $p_x=0$ above.

## Error probability and wrong-answer probability

The probability that an error occurs is not the probability that the final answer is wrong. It depends on what follows the error. In this circuit, $H\,T\,\cdot\,T^\dagger H$ is the identity, so the ideal output is $|0\rangle$.

- $Z$ commutes with $T$, so it reaches the last Hadamard unchanged. $HZH=X$ then flips the result with certainty.
- $X$ does not commute with $T$. The error reaches the end as $H\,T^\dagger X T\,H$, and $T^\dagger X T=(X-Y)/\sqrt2$, so the effective error is $(Z+Y)/\sqrt2$. Acting on $|0\rangle$ it gives $(|0\rangle+i|1\rangle)/\sqrt2$, which yields 0 or 1 with probability 1/2 each.

So with $p_x=p_z=0.2$, $P(1) = 0.2 + 0.2\times 0.5 = 0.3$, not $0.4$. Error correction therefore has to consider which error occurred, not only how often errors occur. The next lesson does this.

## In the lab

The `default.mixed` device simulates the density matrix. In the Bloch spheres tab the vector shortens at the error step and the panel shows the purity. The Register tab shows $P(0)$ and $P(1)$.
