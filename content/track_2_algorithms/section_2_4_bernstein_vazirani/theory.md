## The problem

The hidden function is the bitwise inner product of $x$ with a secret $n$-bit string $s$, modulo 2:

$$
f(x) = s \cdot x = s_0x_0 \oplus s_1x_1 \oplus \dots \oplus s_{n-1}x_{n-1}
$$

Qubit $i$ holds the bit $x_i$, and qubit 0 is the last character of the string. For $s = 1000$ only $s_3 = 1$, so $f(x) = x_3$, and the final state is $|1000\rangle$ with qubit 3 in $|1\rangle$.

The oracle may add a constant bias $b$: $f(x) = s \cdot x \oplus b$. It multiplies the state by the global phase $(-1)^b$ and does not change the result.

Classically, each query returns one bit, so finding $s$ takes $n$ queries (for example $x = 0001, 0010, \dots$). Randomization does not reduce this: $s$ carries $n$ bits and each query gives at most one. The Bernstein–Vazirani algorithm finds $s$ with one query.

## The circuit

The circuit is the one from Deutsch–Jozsa. After the query, the input register is in

$$
\frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

This is the state that Hadamard gates produce from $|s\rangle$:

$$
H^{\otimes n}|s\rangle = \frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

Since $H^{\otimes n}$ is its own inverse, a second layer of Hadamards returns $|s\rangle$, and measuring gives $s$ with certainty.

## Building the oracle

For each $s_i = 1$, the oracle applies a CNOT from qubit $i$ to the auxiliary qubit. With the auxiliary qubit in $|-\rangle$, each CNOT kicks the sign $(-1)^{x_i}$ back onto qubit $i$. The product of these signs is $(-1)^{s\cdot x}$.

## In the lab

In the Amplitudes tab, after the query half of the amplitudes are negative, in a pattern determined by $s$. After the Hadamards all the amplitude is on a single basis state. Read $s$ with qubit 0 on the right. Validation runs your circuit with several hidden strings.

## Qubit ordering

Nielsen & Chuang write qubit 0 on the left of the label, $|x_0 x_1 x_2 x_3\rangle$. Qiskit, and this lab, write qubit 0 on the right, $|q_3 q_2 q_1 q_0\rangle$. Labels in a textbook may appear reversed.
