## Finding a secret string

A box hides an $n$-bit string $s$ and answers, for each input $x$, with the parity of the bits of $x$ where $s$ has a 1:

$$
f(x) = s \cdot x = s_0x_0 \oplus s_1x_1 \oplus \dots \oplus s_{n-1}x_{n-1}
$$

Each answer is one bit, so a classical program needs $n$ queries: ask $0001$, $0010$, $0100$, $1000$ and read $s$ off one bit at a time. Randomization does not help, since $s$ holds $n$ bits and a query gives at most one. The Bernstein–Vazirani algorithm finds $s$ with one query.

Qubit $i$ holds $x_i$ and qubit 0 is the last character of the string, so $s = s_3s_2s_1s_0$ in this lab. For $s = 1000$ only $s_3 = 1$, so $f(x) = x_3$, and the register must end in $|1000\rangle$. The oracle may also add a constant bit $b$, $f(x) = s\cdot x \oplus b$; that only multiplies the state by a global sign $(-1)^b$.

## Why one query is enough

The circuit is the Deutsch–Jozsa circuit: auxiliary qubit in $|-\rangle$, Hadamards on the inputs, one query, Hadamards again. After the query the input register holds

$$
\frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

This state is a product, one qubit at a time, because $(-1)^{s\cdot x} = \prod_i (-1)^{s_ix_i}$. Qubit $i$ is in $|-\rangle$ if $s_i = 1$ and in $|+\rangle$ if $s_i = 0$. For $n=3$ and $s = 101$ the register is $|-\rangle|+\rangle|-\rangle$, and the last layer of Hadamards turns each $|-\rangle$ into $|1\rangle$ and each $|+\rangle$ into $|0\rangle$: the result is $|101\rangle$, with certainty.

To build the oracle, apply a CNOT from qubit $i$ to the auxiliary qubit for every $i$ with $s_i = 1$. With the auxiliary qubit in $|-\rangle$, each CNOT kicks the sign $(-1)^{x_i}$ back onto qubit $i$.
