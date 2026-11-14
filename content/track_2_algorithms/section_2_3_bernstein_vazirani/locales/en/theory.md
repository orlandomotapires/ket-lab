## The problem

Now the secret function is the bitwise product of $x$ with a secret $n$-bit string $s$, modulo 2:

$$
f(x) = s \cdot x = s_0x_0 \oplus s_1x_1 \oplus \dots \oplus s_{n-1}x_{n-1}
$$

Classically, each query reveals one bit of $s$ (by querying $x = 0001$, $0010$, ...), so $n$ queries are needed. The Bernstein-Vazirani algorithm recovers all of $s$ with **one**.

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
