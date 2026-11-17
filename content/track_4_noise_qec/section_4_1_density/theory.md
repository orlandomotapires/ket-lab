## Forty percent of the runs have an error

The circuit $H$, $T$, $T^\dagger$, $H$ is the identity, so it takes $|0\rangle$ to $|0\rangle$. Put an error between the two $T$ gates: $X$ with probability 0.2, $Z$ with probability 0.2, nothing with probability 0.6. An error happens in 40% of the runs. You might expect the final measurement to give the wrong result, 1, in 40% of them. It gives 1 in 30%. To see why, we first need a way to write down a qubit that is in one state or another at random, because no single state vector describes that.

## Mixed states and the density operator

A **pure state** is a single state vector $|\psi\rangle$. When we only know that the qubit is in $|\psi_i\rangle$ with probability $p_i$, it is in a **mixed state**. A mixed state is not a superposition: $(|0\rangle+|1\rangle)/\sqrt2$ has a definite relative phase and gives 0 or 1 at random only in the computational basis, while a coin that yields $|0\rangle$ or $|1\rangle$ with probability 1/2 each has no phase at all, and is random in the $X$ basis as well.

Both cases are described by the **density operator** (density matrix)

$$
\rho = \sum_i p_i\, |\psi_i\rangle\langle\psi_i| ,
$$

which is Hermitian, positive semidefinite and has $\mathrm{Tr}\,\rho = 1$. In the computational basis the diagonal gives the measurement probabilities, $P(0)=\rho_{00}$ and $P(1)=\rho_{11}$. The **purity** $\mathrm{Tr}(\rho^2)$ is 1 for a pure state and smaller for a mixed one, down to $1/2$ for one qubit ($1/d$ in $d$ dimensions). On the Bloch sphere, pure states sit on the surface and mixed states inside; the Bloch vector has length $\sqrt{2\,\mathrm{Tr}(\rho^2)-1}$.

One qubit of an entangled pair is mixed too. Its state is the **reduced density operator**, obtained by the partial trace over the other qubit, and it explains why the Bloch vectors of entangled qubits in Track 1 were shorter than 1.

## Noise as Kraus operators

A noisy operation takes $\rho$ to

$$
\rho \;\longrightarrow\; \sum_k K_k\, \rho\, K_k^\dagger, \qquad \sum_k K_k^\dagger K_k = I ,
$$

where the $K_k$ are the **Kraus operators** (operator-sum representation). A map of this form is called a **quantum channel**. The completeness condition keeps $\mathrm{Tr}\,\rho = 1$. The error above has

$$
K_0 = \sqrt{1-p_x-p_z}\,I, \qquad K_1 = \sqrt{p_x}\,X, \qquad K_2 = \sqrt{p_z}\,Z ,
$$

and indeed $\sum_k K_k^\dagger K_k = (1-p_x-p_z)I + p_xI + p_zI = I$. The square roots are what make the probabilities appear once the sandwich $K\rho K^\dagger$ is formed; with plain $p$ on the operators the sum would not be $I$. The bit flip is the case $p_z=0$ and the phase flip the case $p_x=0$. The depolarizing and amplitude damping channels are two other standard single-qubit channels.

## Where the 30% comes from

Follow each error to the end of the circuit. Before the error the state is $T H|0\rangle$, and afterwards $H T^\dagger$ is applied, so an error $E$ reaches the measurement as $H\,(T^\dagger E T)\,H$.

$Z$ commutes with $T$, so $T^\dagger Z T = Z$, and $HZH = X$. The $Z$ error becomes a bit flip: the result is 1 with certainty.

$X$ does not commute with $T$. A direct multiplication gives $T^\dagger X T = (X-Y)/\sqrt2$, and conjugating with $H$ turns this into $(Z+Y)/\sqrt2$. On $|0\rangle$ it gives $(|0\rangle + i|1\rangle)/\sqrt2$, which yields 0 or 1 with probability 1/2 each.

So $P(1) = 0.2\times 1 + 0.2\times 0.5 = 0.3$. The full state is

$$
\rho = \begin{pmatrix} 0.7 & -0.1i \\ 0.1i & 0.3 \end{pmatrix}, \qquad \mathrm{Tr}(\rho^2) = 0.6 ,
$$

a Bloch vector of length $\sqrt{0.2}\approx 0.45$. The easy slip is to forget that the same Pauli can be harmless or fatal depending on the gates that follow it. A code therefore has to find out which error happened, not only how often errors happen, and the next lesson does exactly that.

## In the lab

Before you run anything, predict $P(1)$ for $p_x = 0.2$, $p_z = 0$, and then for $p_x = 0$, $p_z = 0.2$. Change the two numbers in your code and compare.
