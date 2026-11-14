## Definition

The discrete Fourier transform maps a sequence of numbers to its frequency components. The **quantum Fourier transform** (QFT) applies the same map to the amplitudes of an $n$-qubit state. With $N = 2^n$:

$$
\text{QFT}\,|x\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi i\, xk/N}\,|k\rangle
$$

Every $|k\rangle$ has probability $1/N$. The information about $x$ is in the phases: the amplitude of $|k\rangle$ is rotated by the fraction $xk/N$ of a full turn.

## Product form

Write $k = \sum_j k_j 2^j$. The sum factors into one term per qubit:

$$
\text{QFT}\,|x\rangle = \bigotimes_{j=0}^{n-1} \frac{|0\rangle + e^{2\pi i\, x\, 2^{j}/N}\,|1\rangle}{\sqrt{2}}
$$

where factor $j$ is the state of qubit $j$ in the output. For $n = 3$, qubit 0 has relative phase $x/8$ of a turn, qubit 1 has $x/4$ and qubit 2 has $x/2$. Each qubit lies on the equator of the Bloch sphere. A Hadamard gate puts a qubit on the equator, and controlled phases from the other qubits add the smaller fractions of a turn.

## The circuit

Write $x = 4x_2 + 2x_1 + x_0$. For 3 qubits, starting from the most significant one (qubit 2):

1. $H$ on qubit 2, then a $\pi/2$ phase controlled by qubit 1 and a $\pi/4$ phase controlled by qubit 0. Qubit 2 now has relative phase $x_2/2 + x_1/4 + x_0/8 = x/8$ (mod 1) turns.
2. $H$ on qubit 1, then a $\pi/2$ phase controlled by qubit 0. Its relative phase is $x_1/2 + x_0/4 = x/4$ (mod 1).
3. $H$ on qubit 0. Its relative phase is $x_0/2 = x/2$ (mod 1).
4. `swap` of qubits 0 and 2.

The controlled phase is `qc.cp(angle, control, target)`. It applies

$$
P(\varphi) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\varphi} \end{pmatrix}
$$

to the target when the control is $|1\rangle$.

The swap is needed because steps 1 to 3 put the $x/8$ phase on qubit 2 and the $x/2$ phase on qubit 0, while the QFT output needs them on qubit 0 and qubit 2 respectively. Without the swap, the output qubits appear in reverse order. Here the swap is part of the circuit.

## Qubit ordering

Nielsen & Chuang write qubit 0 on the left of the label. Qiskit, and this lab, write qubit 0 on the right, so $|101\rangle$ has $x_2 = 1$, $x_1 = 0$, $x_0 = 1$ and $x = 5$. Circuit diagrams in a textbook may appear mirrored.

## Relation to the Hadamard transform

For one qubit ($N = 2$) the QFT is the Hadamard gate. The transform $H^{\otimes n}$ is the Fourier transform over $(\mathbb{Z}_2)^n$, with characters $(-1)^{s\cdot x}$, and it is what Bernstein–Vazirani used. The QFT here is the Fourier transform over $\mathbb{Z}_{2^n}$, with phases $e^{2\pi i\,xk/2^n}$.

## In the lab

`prepare_input(qc)` prepares $|x\rangle$, here $|101\rangle = |5\rangle$. The Phases tab shows one dial per basis state: the size gives the probability and the pointer gives the phase. After the QFT, the pointer of $|k\rangle$ is at $5k/8$ of a turn, so it advances by equal steps from one state to the next. Validation runs your circuit with several inputs, including superpositions.
