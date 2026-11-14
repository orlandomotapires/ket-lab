## The problem

A function $f:\{0,1\}^n \to \{0,1\}$ is given as a black box, with a promise: $f$ is either **constant** (the same output for every input) or **balanced** (output $0$ for exactly half of the inputs and $1$ for the other half). The task is to decide which.

A deterministic classical algorithm needs $2^{n-1} + 1$ queries in the worst case: if the first $2^{n-1}$ answers are equal, $f$ can still be balanced. The Deutsch–Jozsa algorithm decides with one query and no error.

This is a separation from exact classical algorithms. A randomized classical algorithm that queries $k$ random inputs and answers "constant" if all outputs agree errs with probability about $2^{1-k}$, which is already small for modest $k$.

## The oracle

The function is available as the query gate $U_f$ (the oracle):

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Here $x$ is the input register (qubits 0 to 2) and $y$ is the auxiliary qubit (qubit 3). In the lab, the oracle is `oracle(qc)` and its contents are hidden.

## The algorithm

1. Prepare the auxiliary qubit in $|-\rangle$ and apply a Hadamard gate to each input qubit, giving a uniform superposition.
2. Query once. By phase kickback, each basis state $|x\rangle$ acquires the sign $(-1)^{f(x)}$:

$$
\frac{1}{\sqrt{2^n}}\sum_x |x\rangle \;\longrightarrow\; \frac{1}{\sqrt{2^n}}\sum_x (-1)^{f(x)}|x\rangle
$$

3. Apply a Hadamard gate to each input qubit. The amplitude of $|0\dots0\rangle$ is the average of the signs:

$$
\frac{1}{2^n}\sum_x (-1)^{f(x)}
$$

If $f$ is constant, the average is $\pm 1$ and the input register is $|0\dots0\rangle$. If $f$ is balanced, the signs cancel and $|0\dots0\rangle$ has probability zero. Measuring the input register decides: all zeros means constant, anything else means balanced.

## In the lab

The Amplitudes tab shows the state of the input register with its signs. Before the last layer of Hadamards, read the signs written by the oracle. After it, the amplitude is either all on $|000\rangle$ or absent from it. The default oracle is balanced. Validation runs your circuit against several hidden oracles, constant and balanced.

## Qubit ordering

Nielsen & Chuang write qubit 0 on the left of the label, $|x_0 x_1 x_2\rangle$. Qiskit, and this lab, write qubit 0 on the right, $|q_2 q_1 q_0\rangle$. Labels in a textbook may appear reversed.
