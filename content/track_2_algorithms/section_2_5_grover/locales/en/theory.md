## Unstructured search

Among $N$ items, exactly one is marked and only an oracle knows which. A classical algorithm needs to check, on average, $N/2$ items. Grover's algorithm finds the marked one with about $\frac{\pi}{4}\sqrt{N}$ queries: a quadratic speedup.

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

Each iteration (oracle and diffuser) rotates the state by an angle $2\theta$ toward $|\omega\rangle$, with $\sin\theta = 1/\sqrt{N}$. With $N = 16$, the ideal is $\left\lfloor \frac{\pi}{4}\sqrt{16} \right\rfloor = 3$ iterations, and the probability of the marked state reaches $96.1\%$. Iterating beyond that overshoots, and the probability drops.

## In the lab

The **Amplitudes** tab shows the 16 amplitudes with sign and the dashed line of the mean. Step through: the oracle pushes the marked bar down and the diffuser throws it above the mean. The marked item here is secret; during validation, the circuit is tested with several marked items.
