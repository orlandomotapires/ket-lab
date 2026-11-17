## Reading a phase that kickback leaves behind

A unitary $U$ has an eigenvector $|\psi\rangle$ with eigenvalue $e^{2\pi i\theta}$, $0 \le \theta < 1$. Phase kickback (lesson 2.1) puts that eigenvalue on a control qubit as a relative phase, where a measurement cannot see it. **Phase estimation** reads $\theta$, given $|\psi\rangle$ and the ability to apply controlled powers of $U$. It is the quantum part of order finding, and so of Shor's algorithm.

Take $t$ counting qubits in $|+\rangle$ and apply $U^{2^j}$ controlled by counting qubit $j$. That qubit gets the relative phase $e^{2\pi i\,2^j\theta}$, and the counting register holds

$$
\frac{1}{\sqrt{2^t}}\sum_{k=0}^{2^t-1} e^{2\pi i\,\theta k}\,|k\rangle
$$

Compare this with the QFT of lesson 2.7. Let $\theta = 3/8$ and $t = 3$. Counting qubit 0 gets $3/8$ of a turn, qubit 1 gets $6/8$ and qubit 2 gets $12/8 \equiv 1/2$. These are the phases of $\text{QFT}\,|3\rangle$, whose qubit $j$ has $3\cdot 2^j/8$ of a turn. So the inverse QFT returns $|3\rangle = |011\rangle$, and $\theta = 3/8$. In general, when $2^t\theta$ is an integer $m$, the register is $\text{QFT}\,|m\rangle$ and the inverse QFT gives $|m\rangle$.

## The circuit

Hadamard gates on the counting qubits (0, 1 and 2) and the eigenvector on qubit 3. For each counting qubit $j$, the controlled power $U^{2^j}$, in the lab `apply_controlled_u(qc, j, 2**j)`. Then `inverse_qft(qc, [0, 1, 2])` and a measurement of the counting register. A result $m$ gives $\theta \approx m/2^t$.

Counting qubit $j$ has weight $2^j$ and Qiskit writes qubit 0 on the right, so a measured string such as `"101"` is read directly with `int(bits, 2)`. A textbook that writes the first qubit on the left shows the string mirrored.

## When $\theta$ is not a multiple of $1/2^t$

With $t = 3$ the resolution is $1/8$. If $\delta = \theta - m/2^t$ is the distance from $\theta$ to the outcome $m$, the probability of measuring $m$ is

$$
P(m) = \frac{\sin^2(\pi\, 2^t \delta)}{2^{2t}\,\sin^2(\pi\delta)}
$$

For $\theta = 0.3$ and $t = 3$: $m = 2$ ($\delta = 0.05$) has probability 0.578, $m = 3$ ($\delta = -0.075$) has 0.259, and the rest is spread over other values. The best outcome always has probability at least $4/\pi^2 \approx 0.405$. With $t = 6$ the best outcome, $19/64 = 0.297$, has probability 0.875. To get $\theta$ correct to $n$ bits with probability at least $1-\epsilon$, use $t = n + \lceil \log_2(2 + \frac{1}{2\epsilon}) \rceil$ counting qubits.

If qubit 3 starts in $|+\rangle$, which is a superposition of the eigenvectors $|0\rangle$ (eigenvalue 1, $\theta = 0$) and $|1\rangle$, the measurement gives $0$ or $\theta$ with probability $1/2$ each.

## In the lab

$U$ is a phase gate, $\mathrm{diag}(1, e^{2\pi i\theta})$, with eigenvector $|1\rangle$, and $\theta$ is hidden. `run_shots(qc)` returns the counts for 1024 runs, from which you compute `theta`.
