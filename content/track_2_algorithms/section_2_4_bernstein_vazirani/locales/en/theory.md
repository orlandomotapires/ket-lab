## The problem

Now the secret function is the bitwise product of $x$ with a secret $n$-bit string $s$, modulo 2:

$$
f(x) = s \cdot x = s_0x_0 \oplus s_1x_1 \oplus \dots \oplus s_{n-1}x_{n-1}
$$

Ordering convention: qubit $i$ holds the bit $x_i$, and qubit 0 is the **last** character of the string. If $s = 1000$, only $s_3 = 1$ and $f(x) = x_3$; the final state is $|1000\rangle$, with qubit 3 in $|1\rangle$.

The oracle may also add a bias $b$: $f(x) = s \cdot x \oplus b$. The $b$ only multiplies the state by a global phase $(-1)^b$ and does not change the answer.

Classically, each query reveals one bit of $s$ (by querying $x = 0001$, $0010$, ...), so $n$ queries are needed. Randomness does not help: each query gives at most 1 bit of information and $s$ has $n$ bits, so with fewer than $n$ queries you cannot succeed with high probability. The Bernstein-Vazirani algorithm recovers all of $s$ with **one**.

## The same circuit, another reading

The circuit is the Deutsch-Jozsa one. After the oracle, the input register is in

$$
\frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

and this is exactly the state that the Hadamards produce from $|s\rangle$:

$$
H^{\otimes n}|s\rangle = \frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

Since the Hadamard undoes itself ($HH = I$), the last layer of Hadamards returns $|s\rangle$. Measuring gives $s$ with certainty.

## How the oracle is built

For each bit $s_i = 1$, the oracle applies a CNOT from qubit $i$ to the auxiliary qubit. With the auxiliary in $|-\rangle$, each of these CNOTs returns the sign $(-1)^{x_i}$ to qubit $i$: phase kickback again.

## In the lab

In the **Amplitudes** tab, after the oracle half of the signs are negative, in a pattern that encodes $s$. After the Hadamards, all the amplitude concentrates in a single state. Read $s$ with qubit 0 on the right. During validation, the circuit is tested with several secret strings.

## A note on notation

Many textbooks write qubit 0 on the **left** of the label, as in $|x_0 x_1 x_2\rangle$. Qiskit, and therefore this lab, writes qubit 0 on the **right**: $|q_2 q_1 q_0\rangle$. When comparing with a textbook, labels may appear reversed.
