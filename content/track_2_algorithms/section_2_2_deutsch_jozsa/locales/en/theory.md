## The problem

You are given a function $f:\{0,1\}^n \to \{0,1\}$ as a black box, with a promise: it is either **constant** (the same output for every input) or **balanced** (output $0$ for half of the inputs and $1$ for the other half). Which one is it?

A classical algorithm needs, in the worst case, $2^{n-1} + 1$ queries: if the first $2^{n-1}$ give the same value, the function can still be balanced. The Deutsch-Jozsa algorithm answers with **a single query**.

## The oracle

The function enters the circuit as a gate, the **oracle**:

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Here $x$ is the input register (qubits 0 to 2) and $y$ is an auxiliary qubit (qubit 3). In the lab, the oracle is the function `oracle(qc)`, and its contents are secret.

## The algorithm

1. Auxiliary qubit in $|-\rangle$ and input in uniform superposition, using Hadamards.
2. One query to the oracle. By phase kickback, each term picks up the sign $(-1)^{f(x)}$:

$$
\frac{1}{\sqrt{2^n}}\sum_x |x\rangle \;\longrightarrow\; \frac{1}{\sqrt{2^n}}\sum_x (-1)^{f(x)}|x\rangle
$$

3. Hadamards again on the input. The final amplitude of $|00\dots0\rangle$ is the average of the signs:

$$
\frac{1}{2^n}\sum_x (-1)^{f(x)}
$$

If $f$ is constant, this average is $\pm 1$ and the input ends in $|000\rangle$ with certainty. If it is balanced, the signs cancel and $|000\rangle$ has probability zero. One measurement decides.

## In the lab

The **Amplitudes** tab shows the state of the input register, with sign. Before the last layer of Hadamards, look at the signs the oracle imprinted; after it, watch interference concentrate all the amplitude in $|000\rangle$ or wipe it out. The oracle in this lab is balanced. During validation, your circuit is tested against several secret oracles, constant and balanced.
