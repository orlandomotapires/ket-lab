## Unstructured search

Among $N$ items, some are marked ($M$ of them in total) and only an oracle knows which. A classical algorithm needs to check, on average, $N/2$ items. Grover's algorithm finds the marked one with about $\frac{\pi}{4}\sqrt{N}$ queries: a quadratic speedup.

## The phase oracle

Here the oracle flips the sign of the marked state $|\omega\rangle$ only:

$$
U_\omega|x\rangle = \begin{cases} -|x\rangle & \text{if } x = \omega \\ \phantom{-}|x\rangle & \text{if } x \neq \omega \end{cases}
$$

On its own, this flip does not change any probability.

## The diffuser: inversion about the mean

The **diffuser** $D = 2|s\rangle\langle s| - I$, where $|s\rangle$ is the uniform superposition, reflects each amplitude about the mean of all of them:

$$
a_x \;\longrightarrow\; 2\bar{a} - a_x
$$

After the oracle, the marked amplitude is negative and pulls the mean down a little. The reflection throws it well above the mean, and the others shrink slightly.

In the circuit, $D = H^{\otimes n}\,(2|0\rangle\langle 0| - I)\,H^{\otimes n}$. The reflection about $|0000\rangle$ is done, up to a global phase, with $X$ on all qubits, a multi-controlled $Z$ and $X$ again. The multi-controlled $Z$ comes from a generalized Toffoli between two Hadamards:

```python
qc.h(3)
qc.mcx([0, 1, 2], 3)
qc.h(3)
```

## How many iterations

With $M$ marked items among $N$, $\sin\theta = \sqrt{M/N}$. Each iteration (oracle and diffuser) rotates the state by an angle $2\theta$ toward the subspace of marked items; after $k$ iterations, the success probability is $\sin^2\big((2k+1)\theta\big)$. The best $k$ is

$$
k = \left\lfloor \frac{\pi}{4}\sqrt{\frac{N}{M}} \right\rfloor
$$

With $N = 16$:

| $M$ | $k$ | success probability |
| :-: | :-: | :-: |
| 1 | 3 | $96.1\%$ |
| 2 | 2 | $94.5\%$ |
| 4 | 1 | $100\%$ |

Iterating beyond the ideal overshoots, and the probability drops. That is why a search that does not know $M$ has to estimate it first (for example, with quantum counting, which uses phase estimation).

## Limits

The speedup is **quadratic** ($\sqrt{N}$ against $N$), not exponential, and it is optimal for unstructured search. Grover also does **not** make NP-complete problems easy: for them, $2^{n/2}$ queries are still needed, which remains exponential in $n$.

## In the lab

The **Amplitudes** tab shows the 16 amplitudes with sign and the dashed line of the mean. Step through: the oracle pushes the marked bar down and the diffuser throws it above the mean. The marked item here is secret; during validation, the circuit is tested with several marked items.
