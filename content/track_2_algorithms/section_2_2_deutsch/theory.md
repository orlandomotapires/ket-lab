## One query instead of two

A sealed box computes a function $f$ from one bit to one bit. It is one of four: always 0, always 1, a copy of its input, or the negation of its input. You are not asked which one, only whether $f$ is **constant** ($f(0) = f(1)$) or **balanced** ($f(0) \neq f(1)$). A classical program has to call the box twice, once for each input. Deutsch's algorithm calls it once.

On a quantum computer the box is a gate, the **query gate** $U_f$, which uses two qubits:

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Here $x$ is qubit 0 (the input) and $y$ is qubit 1 (the auxiliary qubit), and $\oplus$ is addition modulo 2. One use of $U_f$ is one **query**; in the lab it is `oracle(qc)`, and its inside is hidden.

## Why superposition alone gives nothing

Put the input in $|+\rangle$ and the auxiliary qubit in $|0\rangle$. One query gives

$$
\frac{1}{\sqrt2}\big(|0\rangle|f(0)\rangle + |1\rangle|f(1)\rangle\big)
$$

Both values of $f$ are in the state, but the input is entangled with the auxiliary qubit. Measuring the input gives 0 or 1 with probability $1/2$, whatever $f$ is.

## Moving the answer into a sign

With the auxiliary qubit in $|-\rangle$ the same query is a phase kickback (lesson 2.1). If $f(x) = 0$ the auxiliary qubit is unchanged; if $f(x) = 1$ the query swaps $|0\rangle$ and $|1\rangle$ in it, which turns $|-\rangle$ into $-|-\rangle$. So the query multiplies $|x\rangle|-\rangle$ by $(-1)^{f(x)}$, and the input is left in

$$
\frac{1}{\sqrt2}\big((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle\big)
$$

Run the four boxes. For $f(x) = x$ the input is $(|0\rangle - |1\rangle)/\sqrt2 = |-\rangle$. For $f(x) = 1 \oplus x$ it is $(-|0\rangle + |1\rangle)/\sqrt2 = -|-\rangle$. For the constant boxes it is $|+\rangle$ or $-|+\rangle$. The two balanced boxes differ from each other only by a global sign, and so do the two constant ones.

A Hadamard gate on the input now separates the cases: $|+\rangle$ becomes $|0\rangle$ and $|-\rangle$ becomes $|1\rangle$, up to sign. Measuring qubit 0 gives $f(0) \oplus f(1)$ with certainty, which is 0 for constant and 1 for balanced.

The algorithm does not tell you $f(0)$ or $f(1)$; the boxes $x$ and $1 \oplus x$ give the same outcome. One query is enough because the question asks for less than the whole function. A common slip is to leave out the final Hadamard: the relative sign is invisible to a measurement in the computational basis, and you get a coin flip.
