## Why a Fourier transform

A measurement returns one value, so you cannot read a period from a quantum state by measuring it. The discrete Fourier transform turns a list that repeats with period $r$ into a list with peaks spaced $N/r$ apart, and peaks can be measured. The **quantum Fourier transform** (QFT) applies that transform to the amplitudes of an $n$-qubit state, with $N = 2^n$. Phase estimation (2.8) and Shor's algorithm (2.9) depend on it.

On a basis state $|x\rangle$ it acts as

$$
\text{QFT}\,|x\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi i\, xk/N}\,|k\rangle
$$

Every $|k\rangle$ has probability $1/N$, and the information about $x$ is in the phases: the amplitude of $|k\rangle$ is rotated by $xk/N$ of a full turn. For $N = 8$ and $x = 5$ the phases of $|0\rangle, |1\rangle, \dots, |7\rangle$ are $0, \tfrac58, \tfrac28, \tfrac78, \tfrac48, \tfrac18, \tfrac68, \tfrac38$ of a turn: $5k/8$ reduced modulo 1.

## Product form and the circuit

Write $k = \sum_j k_j 2^j$. The sum factors into one term per qubit:

$$
\text{QFT}\,|x\rangle = \bigotimes_{j=0}^{n-1} \frac{|0\rangle + e^{2\pi i\, x\, 2^{j}/N}\,|1\rangle}{\sqrt{2}}
$$

where factor $j$ is the output state of qubit $j$. For $n = 3$ and $x = 5$, qubit 0 has relative phase $5/8$ of a turn, qubit 1 has $5/4 \equiv 1/4$ and qubit 2 has $5/2 \equiv 1/2$, so qubit 2 is in $|-\rangle$. Each qubit lies on the equator of the Bloch sphere.

Qiskit writes qubit 0 on the right, so $|101\rangle$ has $x_2 = 1$, $x_1 = 0$, $x_0 = 1$ and $x = 5$. With $x = 4x_2 + 2x_1 + x_0$, build the circuit from the most significant qubit down:

1. $H$ on qubit 2, then a $\pi/2$ phase controlled by qubit 1 and a $\pi/4$ phase controlled by qubit 0. Qubit 2 now has relative phase $x_2/2 + x_1/4 + x_0/8 = x/8$ (mod 1) turns.
2. $H$ on qubit 1, then a $\pi/2$ phase controlled by qubit 0. Its relative phase is $x_1/2 + x_0/4 = x/4$.
3. $H$ on qubit 0, with relative phase $x_0/2 = x/2$.
4. A swap of qubits 0 and 2.

The controlled phase is `qc.cp(angle, control, target)`, which applies $P(\varphi) = \mathrm{diag}(1, e^{i\varphi})$ to the target when the control is $|1\rangle$. The swap is the step people forget: steps 1 to 3 leave the $x/8$ phase on qubit 2 and the $x/2$ phase on qubit 0, and the QFT needs them the other way round.

For one qubit the QFT is the Hadamard gate. The transform $H^{\otimes n}$, used in Bernstein–Vazirani, is the Fourier transform over $(\mathbb{Z}_2)^n$ with characters $(-1)^{s\cdot x}$; the QFT is the one over $\mathbb{Z}_{2^n}$ with phases $e^{2\pi i\,xk/2^n}$.

## In the lab

`prepare_input(qc)` prepares $|101\rangle$. Before you look at the dials, say where the pointer of $|k\rangle$ should be after the QFT, using the list of phases above, and then compare.
