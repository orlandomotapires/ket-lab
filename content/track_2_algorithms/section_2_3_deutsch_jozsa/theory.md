## Eight inputs, one query

Now the box takes 3 bits. The promise is that $f:\{0,1\}^3 \to \{0,1\}$ is either **constant** (the same output for all 8 inputs) or **balanced** (0 on exactly four inputs and 1 on the other four). A classical program that gets four 0s in a row still cannot decide, because the other four inputs could all give 1. In the worst case it needs $2^{n-1} + 1 = 5$ queries for $n = 3$ bits, and $2^{n-1}+1$ in general. The Deutsch–Jozsa algorithm decides with one query and never errs.

Only the exact classical algorithm is beaten. A randomized one that asks $k$ random inputs and answers "constant" when they all agree is wrong with probability about $2^{1-k}$, so ten queries already bring the error below 0.2%. The separation is real but modest.

## The circuit of lesson 2.2, with more qubits

The oracle is the query gate $U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$, with the input register on qubits 0 to 2 and the auxiliary qubit on qubit 3. Put the auxiliary qubit in $|-\rangle$ and a Hadamard on each input qubit. By phase kickback the query writes a sign on every basis state:

$$
\frac{1}{\sqrt{2^n}}\sum_x |x\rangle \;\longrightarrow\; \frac{1}{\sqrt{2^n}}\sum_x (-1)^{f(x)}|x\rangle
$$

A second layer of Hadamards sends the amplitude of $|0\dots0\rangle$ to the average of the signs:

$$
\frac{1}{2^n}\sum_x (-1)^{f(x)}
$$

For a constant $f$ the average is $\pm 1$, so the register ends in $|0\dots0\rangle$. For a balanced $f$ four signs are $+$ and four are $-$, the average is 0, and $|0\dots0\rangle$ never appears. Any other outcome means balanced.

Take two input bits to see it whole, with $f(x) = x_0$. Qiskit writes qubit 0 on the right, so the states $|00\rangle, |01\rangle, |10\rangle, |11\rangle$ get the signs $+,-,+,-$, and the state after the query is $|+\rangle|-\rangle$. The Hadamards turn it into $|0\rangle|1\rangle$, which is the label $|01\rangle$: not all zeros, so balanced. Textbooks that put qubit 0 on the left write the same state as $|10\rangle$.

The algorithm works for every balanced function, not only parities such as $x_0 \oplus x_1$. The check in this lab also runs your circuit on functions like $x_0 \oplus x_1x_2$ and the majority of the three bits.
