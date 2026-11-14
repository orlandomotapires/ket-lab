## The problem

A function $f:\{0,1\} \to \{0,1\}$ sits in a black box. There are four possibilities:

| $f$ | $f(0)$ | $f(1)$ | type |
| :-- | :-: | :-: | :-- |
| $0$ | 0 | 0 | constant |
| $1$ | 1 | 1 | constant |
| $x$ | 0 | 1 | balanced |
| $\text{NOT } x$ | 1 | 0 | balanced |

The question is not which $f$ it is, but whether it is **constant** or **balanced**. Classically you need two queries, $f(0)$ and $f(1)$. Deutsch's algorithm answers with **one**.

## The oracle

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Here $x$ is qubit 0 and $y$ is the auxiliary qubit (qubit 1). In the lab, the oracle is `oracle(qc)`, and its contents are secret.

## Why parallelism alone is not enough

With the input in $|+\rangle$ and the auxiliary qubit in $|0\rangle$, the oracle evaluates $f$ on both inputs at once:

$$
\frac{1}{\sqrt2}\big(|0\rangle|f(0)\rangle + |1\rangle|f(1)\rangle\big)
$$

But measuring just destroys the superposition and returns the value of $f$ at a randomly chosen input. Interference is missing.

## The algorithm

1. Auxiliary qubit in $|-\rangle$, input in $|+\rangle$.
2. One query. By phase kickback, the input becomes
$$
\frac{1}{\sqrt2}\big((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle\big)
$$
3. Hadamard on the input. If $f(0) = f(1)$, the signs agree, the state is $\pm|+\rangle$ and the Hadamard takes it to $|0\rangle$. If $f(0) \neq f(1)$, the state is $\pm|-\rangle$ and the Hadamard takes it to $|1\rangle$.

Measuring qubit 0 gives $f(0) \oplus f(1)$ with certainty.

## What the algorithm reveals

The functions $f = x$ and $f = \text{NOT } x$ give the **same** answer ($|1\rangle$): they differ by a global sign, which is not observable. The algorithm reveals neither $f(0)$ nor $f(1)$, only the global property $f(0) \oplus f(1)$. Trading two queries for one is possible precisely because the question is less demanding than "which $f$ is it?".

## In the lab

In the **Amplitudes** tab, see the sign the oracle imprints on qubit 0 and how the last Hadamard turns it into $|0\rangle$ or $|1\rangle$. During validation, your circuit is tested against all four functions.
