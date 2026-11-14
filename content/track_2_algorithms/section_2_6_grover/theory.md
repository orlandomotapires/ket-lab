## Unstructured search

Among $N$ items, $M$ are marked and only an oracle can tell which. A classical algorithm must check about $N/2$ items on average to find a marked one when $M = 1$. Grover's algorithm needs about $\frac{\pi}{4}\sqrt{N}$ queries, a quadratic speedup.

## The phase oracle

The oracle flips the sign of each marked state $|\omega\rangle$ and leaves the others unchanged:

$$
U_\omega|x\rangle = \begin{cases} -|x\rangle & \text{if } x \text{ is marked} \\ \phantom{-}|x\rangle & \text{otherwise} \end{cases}
$$

By itself this changes no measurement probability, since only the sign of an amplitude changes.

## The diffusion operator

The **diffusion operator** $D = 2|s\rangle\langle s| - I$, with $|s\rangle$ the uniform superposition, reflects every amplitude about their mean (inversion about the mean):

$$
a_x \;\longrightarrow\; 2\bar{a} - a_x
$$

After the oracle, a marked amplitude is negative and lowers the mean slightly. The inversion sends it to a value well above the mean, and the other amplitudes decrease slightly.

In the circuit, $D = H^{\otimes n}\,(2|0\rangle\langle 0| - I)\,H^{\otimes n}$. The reflection $2|0\rangle\langle 0| - I$ equals, up to a global phase, $X^{\otimes n}$ followed by a multi-controlled $Z$ followed by $X^{\otimes n}$. The multi-controlled $Z$ is a multi-controlled NOT between two Hadamards on the target:

```python
qc.h(3)
qc.mcx([0, 1, 2], 3)
qc.h(3)
```

## Number of iterations

A **Grover iteration** is one oracle query followed by the diffusion operator. With $M$ marked items among $N$, let $\sin\theta = \sqrt{M/N}$. Each iteration rotates the state by $2\theta$ toward the uniform superposition of the marked items. After $k$ iterations the probability of measuring a marked item is

$$
\sin^2\big((2k+1)\theta\big)
$$

This is largest near $(2k+1)\theta = \pi/2$, so

$$
k = \left\lfloor \frac{\pi}{4}\sqrt{\frac{N}{M}} \right\rfloor
$$

For $N = 16$:

| $M$ | $k$ | success probability |
| :-: | :-: | :-: |
| 1 | 3 | $96.1\%$ |
| 2 | 2 | $94.5\%$ |
| 4 | 1 | $100\%$ |

More iterations than this rotate past the target and the probability decreases. A search that does not know $M$ must first estimate it, for example with quantum counting, which uses phase estimation.

## Limits

The speedup is quadratic ($\sqrt{N}$ against $N$), and it is optimal for unstructured search. Grover's algorithm does not make NP-complete problems tractable: searching over $n$-bit candidates still takes about $2^{n/2}$ queries, which is exponential in $n$.

## In the lab

The Amplitudes tab shows the 16 amplitudes with sign, and a dashed line at their mean. Step through the circuit: the oracle pushes the marked amplitude below zero and the diffusion operator sends it above the mean. The marked items are hidden. Validation runs your circuit with several sets of marked items.
