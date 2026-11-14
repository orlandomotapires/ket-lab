## The problem

A function $f:\{0,1\} \to \{0,1\}$ is hidden in a black box. There are four possibilities:

| $f$ | $f(0)$ | $f(1)$ | type |
| :-- | :-: | :-: | :-- |
| $0$ | 0 | 0 | constant |
| $1$ | 1 | 1 | constant |
| $x$ | 0 | 1 | balanced |
| $\text{NOT } x$ | 1 | 0 | balanced |

The task is to decide whether $f$ is **constant** ($f(0) = f(1)$) or **balanced** ($f(0) \neq f(1)$). A classical algorithm needs two queries, $f(0)$ and $f(1)$. Deutsch's algorithm needs one.

## The oracle

A **query** to $f$ is one use of the query gate $U_f$:

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Here $x$ is qubit 0 (the input) and $y$ is qubit 1 (the auxiliary qubit). In the lab, the oracle is `oracle(qc)` and its contents are hidden.

## Superposition is not enough

With the input in $|+\rangle$ and the auxiliary qubit in $|0\rangle$, one query gives

$$
\frac{1}{\sqrt2}\big(|0\rangle|f(0)\rangle + |1\rangle|f(1)\rangle\big)
$$

This state contains both values, but the input is entangled with the auxiliary qubit. Measuring the input returns 0 or 1 with probability $1/2$ each, whatever $f$ is.

## The algorithm

1. Prepare the auxiliary qubit in $|-\rangle$ and the input in $|+\rangle$.
2. Query once. By phase kickback, the input becomes
$$
\frac{1}{\sqrt2}\big((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle\big)
$$
and the auxiliary qubit stays in $|-\rangle$.
3. Apply a Hadamard gate to the input. If $f(0) = f(1)$ the state is $\pm|+\rangle$ and the result is $|0\rangle$ up to sign. If $f(0) \neq f(1)$ the state is $\pm|-\rangle$ and the result is $|1\rangle$ up to sign.

Measuring qubit 0 gives $f(0) \oplus f(1)$ with certainty: 0 for constant, 1 for balanced.

## What the answer contains

The functions $x$ and $\text{NOT } x$ both give $|1\rangle$, because they differ only by a global sign. The algorithm does not give $f(0)$ or $f(1)$, only their parity $f(0) \oplus f(1)$. One query suffices because the question asks for less than the full function.

## In the lab

In the Amplitudes tab, follow the sign that the oracle writes on qubit 0 and how the last Hadamard turns it into $|0\rangle$ or $|1\rangle$. Validation runs your circuit against all four functions.
