## Searching without structure

Sixteen boxes hide one prize, and the only way to learn anything is to ask the oracle about a box. Classically you open about 8 boxes on average. Grover's algorithm finds the prize with about $\frac{\pi}{4}\sqrt{16} \approx 3$ oracle calls. For $N$ items the cost is about $\frac{\pi}{4}\sqrt{N}$, a quadratic speedup, and $M$ of the items may be marked.

The oracle flips the sign of each marked state $|\omega\rangle$ and leaves the others alone. By itself it changes no probability, because only the sign of an amplitude moves. The second ingredient is the **diffusion operator**

$$
D = 2|s\rangle\langle s| - I
$$

where $|s\rangle$ is the uniform superposition and $|s\rangle\langle s|$ is the outer product of $|s\rangle$ with itself: the operator that sends $|\psi\rangle$ to $\langle s|\psi\rangle\,|s\rangle$, the projection onto $|s\rangle$. $D$ reflects the state about $|s\rangle$. On the amplitudes this is an inversion about the mean, $a_x \to 2\bar a - a_x$.

## The smallest case by hand

Take $N = 4$ (two qubits) with one marked item. The four amplitudes start at $\tfrac12$. The oracle makes the marked one $-\tfrac12$, so the mean is $\bar a = (3\cdot\tfrac12 - \tfrac12)/4 = \tfrac14$. The inversion sends the marked amplitude to $2\cdot\tfrac14 + \tfrac12 = 1$ and each other one to $2\cdot\tfrac14 - \tfrac12 = 0$. One iteration finds the item with certainty.

In the circuit, $D = H^{\otimes n}(2|0\rangle\langle 0| - I)H^{\otimes n}$. The reflection $2|0\rangle\langle 0| - I$ is, up to a global phase, $X^{\otimes n}$, then a Z controlled by all qubits, then $X^{\otimes n}$ again. The controlled Z is a multi-controlled NOT between two Hadamards on the target:

```python
qc.h(3)
qc.mcx([0, 1, 2], 3)
qc.h(3)
```

## How many iterations

A **Grover iteration** is one oracle call followed by $D$. Let $\sin\theta = \sqrt{M/N}$. Each iteration rotates the state by $2\theta$ toward the marked items, and after $k$ iterations the success probability is $\sin^2((2k+1)\theta)$. It peaks when $(2k+1)\theta$ is closest to $\pi/2$, so the exact rule is that $k$ is the integer nearest to $\frac{\pi}{4\theta} - \frac12$.

When $M$ is much smaller than $N$, $\theta \approx \sqrt{M/N}$ and the rule becomes the familiar $k = \lfloor \frac{\pi}{4}\sqrt{N/M} \rfloor$. For $N = 16$ this gives 3 iterations for $M = 1$ (probability 96.1%), 2 for $M = 2$ (94.5%) and 1 for $M = 4$ (100%). It fails when $M$ is a sizeable fraction of $N$: with $M = 8$ the probability is $1/2$ for every $k$, and with $M = 9$ one iteration lowers it from 56% to 32%.

Past the peak the state rotates beyond the target and the probability falls; for $M=1$, six iterations leave 2%. If $M$ is unknown it has to be estimated first, for example with quantum counting, which uses phase estimation (lesson 2.8).

## Limits

The speedup is quadratic and optimal for unstructured search. It does not make NP-complete problems easy: searching over $n$-bit candidates still takes about $2^{n/2}$ queries.
