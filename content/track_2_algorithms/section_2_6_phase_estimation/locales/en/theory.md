## The problem

A unitary operator $U$ has an eigenvector $|\psi\rangle$ with eigenvalue $e^{2\pi i\theta}$:

$$
U|\psi\rangle = e^{2\pi i\theta}|\psi\rangle, \qquad 0 \le \theta < 1
$$

**Phase estimation** finds $\theta$. It is the heart of Shor's algorithm and of many chemistry simulations.

## The idea

By phase kickback, a controlled $U$ with the target in $|\psi\rangle$ returns the phase $e^{2\pi i\theta}$ to the control. Applying $U^{2^j}$ controlled by counting qubit $j$, that qubit picks up the phase $e^{2\pi i\,2^j\theta}$. With $t$ counting qubits, the register ends up in

$$
\frac{1}{\sqrt{2^t}}\sum_{k=0}^{2^t-1} e^{2\pi i\,\theta k}\,|k\rangle
$$

which is exactly the QFT of the number $2^t\theta$. The inverse QFT gives that number back.

## The circuit

1. Hadamard on the counting qubits (0, 1 and 2) and the eigenvector on qubit 3.
2. For each counting qubit $j$, the controlled power $U^{2^j}$: `apply_controlled_u(qc, j, 2**j)`.
3. The inverse QFT from the previous lesson: `inverse_qft(qc, [0, 1, 2])`.
4. Measure the counting register. The value read $m$ gives $\theta \approx m/2^t$.

With $t = 3$, the precision is $1/8$. When $\theta$ is not a multiple of $1/8$, the result spreads around the nearest value; more counting qubits narrow that peak.

## In this lab

$U$ is a phase gate, $U = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i\theta} \end{pmatrix}$, whose eigenvector is $|1\rangle$. The value of $\theta$ is secret. After measuring, `run_shots(qc)` runs the circuit 1024 times and returns the counts; use them to compute `theta` in Python. The **Register** tab shows the probability of each counting value, with the corresponding fraction.
