## The problem

A unitary operator $U$ has an eigenvector $|\psi\rangle$ with eigenvalue $e^{2\pi i\theta}$:

$$
U|\psi\rangle = e^{2\pi i\theta}|\psi\rangle, \qquad 0 \le \theta < 1
$$

**Phase estimation** computes $\theta$, given the ability to apply controlled powers of $U$ and to prepare $|\psi\rangle$. It is the quantum part of order finding, and so of Shor's algorithm.

## The idea

By phase kickback, a controlled-$U$ with the target in $|\psi\rangle$ applies the phase $e^{2\pi i\theta}$ to the $|1\rangle$ term of the control. Take $t$ counting qubits in $|+\rangle$ and apply $U^{2^j}$ controlled by counting qubit $j$. That qubit acquires the relative phase $e^{2\pi i\,2^j\theta}$, and the counting register is in

$$
\frac{1}{\sqrt{2^t}}\sum_{k=0}^{2^t-1} e^{2\pi i\,\theta k}\,|k\rangle
$$

This is the QFT of the basis state $|2^t\theta\rangle$, when $2^t\theta$ is an integer. The inverse QFT therefore returns $|2^t\theta\rangle$.

## The circuit

1. Hadamard gates on the counting qubits (0, 1 and 2) and the eigenvector $|\psi\rangle$ on qubit 3.
2. For each counting qubit $j$, the controlled power $U^{2^j}$: `apply_controlled_u(qc, j, 2**j)`.
3. The inverse QFT from the previous lesson: `inverse_qft(qc, [0, 1, 2])`.
4. Measure the counting register. A result $m$ gives $\theta \approx m/2^t$.

With $t = 3$ the resolution is $1/8$. If $\theta$ is a multiple of $1/8$, the result is exact. Otherwise the probability concentrates on the values nearest to $2^t\theta$, and more counting qubits give a finer estimate.

## Qubit ordering

Counting qubit $j$ is the bit of weight $2^j$, so qubit 0 is the least significant bit. Nielsen & Chuang write the most significant bit first, with the first qubit on the left. Qiskit, and this lab, write qubit 0 on the right, so a measured string such as `"101"` is read directly with `int(bits, 2)`.

## An input that is not an eigenvector

Suppose qubit 3 starts in $|+\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$. This is a superposition of two eigenvectors of $U$: $|0\rangle$ with eigenvalue $1$ ($\theta = 0$) and $|1\rangle$ with eigenvalue $e^{2\pi i\theta}$. The measurement gives $0$ or $\theta$, with probability $1/2$ each.

## In the lab

$U$ is a phase gate, $U = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i\theta} \end{pmatrix}$, with eigenvector $|1\rangle$. The value of $\theta$ is hidden. `run_shots(qc)` runs the circuit 1024 times and returns the counts, from which you compute `theta` in Python. The Register tab shows the probability of each counting value and the fraction it represents.
