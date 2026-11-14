## From position to frequency

The discrete Fourier transform takes a sequence of numbers to its frequency spectrum. The **quantum Fourier transform** (QFT) does the same with the amplitudes of an $n$-qubit state, with $N = 2^n$:

$$
\text{QFT}\,|x\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi i\, xk/N}\,|k\rangle
$$

All outputs have the same probability, $1/N$. The information about $x$ lives entirely in the **phases**: the amplitude of $|k\rangle$ rotates by $xk/N$ of a full turn.

## The product form

The same expression factors qubit by qubit: each qubit ends up on the equator of the Bloch sphere, with a phase proportional to $x$. One of them rotates by $x/2$ of a turn, another by $x/4$, another by $x/8$. This form is what gives the circuit: a Hadamard creates the equator, and phases controlled by the other qubits add the smaller fractions.

## The circuit

For 3 qubits, starting with the most significant one (qubit 2):

1. $H$ on qubit 2; then the $\pi/2$ phase controlled by qubit 1 and the $\pi/4$ phase controlled by qubit 0.
2. $H$ on qubit 1; then the $\pi/2$ phase controlled by qubit 0.
3. $H$ on qubit 0.
4. `swap` between qubits 0 and 2: the circuit produces the qubits in reverse order.

The controlled phase is `qc.cp(angle, control, target)`, the gate

$$
R(\varphi) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\varphi} \end{pmatrix}
$$

applied to the target when the control is $1$.

## In the lab

The function `prepare_input(qc)` prepares the input $|x\rangle$, here $|101\rangle = |5\rangle$. The **Phases** tab shows one dial per state: the size indicates the probability and the pointer, the phase. After the QFT, the pointers rotate by $5k/8$ of a turn, advancing in equal steps from one state to the next. During validation, the circuit is tested with several inputs, including superpositions.
