## Cutting a graph with a circuit

Five vertices, six edges, and the task is to color each vertex with one of two colors so that as many edges as possible join different colors. These are the **cut** edges. The graph of this lesson contains the triangle 0–1–4, and no coloring cuts all three edges of a triangle, so the best cut has 5 edges, not 6. This is Max-Cut, and it is NP-hard: no efficient exact algorithm is known for large graphs. A coloring picked at random cuts each edge with probability $\frac12$, so on average 3 of the 6 edges, a ratio of $3/5 = 0.6$ to the best. QAOA starts there and tries to climb.

Give each vertex a qubit, with $|0\rangle$ or $|1\rangle$ as its color. An edge $(i,j)$ is cut when the bits differ, that is when $Z_iZ_j = -1$, so

$$
\text{cut} = \sum_{(i,j)} \frac{1 - Z_i Z_j}{2}.
$$

Maximizing the cut is the same as minimizing the Ising energy $H_C = \sum_{(i,j)} Z_i Z_j$, the **cost Hamiltonian** (`cost_h` in the lab). For a state with $\langle H_C\rangle = E$ the expected cut on this graph is $(6 - E)/2$.

## Two unitaries, applied in turns

The **quantum approximate optimization algorithm** starts from the uniform superposition $|+\rangle^{\otimes n}$, where every coloring has probability $1/32$, and applies $p$ layers of a cost unitary and a mixer unitary:

$$
|\vec\gamma, \vec\beta\rangle = U_M(\beta_p)\,U_C(\gamma_p) \cdots U_M(\beta_1)\,U_C(\gamma_1)\,|+\rangle^{\otimes n}.
$$

The cost unitary $U_C(\gamma) = e^{-i\gamma H_C/2}$ is an IsingZZ($\gamma$) gate on each edge. The mixer $U_M(\beta) = e^{-i\beta \sum_k X_k}$ is $R_X(2\beta)$ on each qubit. A classical optimizer adjusts the $2p$ angles to minimize $\langle H_C\rangle$, the loop of lesson 3.1.

The cost layer alone does nothing you can measure. $H_C$ is diagonal in the computational basis, so $U_C$ multiplies each coloring $|z\rangle$ by a phase $e^{-i\gamma E(z)/2}$, and all 32 probabilities stay at $1/32$. The mixer $\sum_k X_k$ does not commute with $H_C$, so it makes the phases interfere and turns phase differences into probability differences.

Take one edge, two qubits and $p = 1$ to see this. After the Hadamards the state is $\frac12(|00\rangle+|01\rangle+|10\rangle+|11\rangle)$. IsingZZ($\gamma$) multiplies $|00\rangle$ and $|11\rangle$ by $e^{-i\gamma/2}$ and the cut states $|01\rangle$ and $|10\rangle$ by $e^{+i\gamma/2}$, and the probabilities are still $\frac14$ each. After $R_X(2\beta)$ on both qubits, $\langle ZZ\rangle = \sin\gamma\,\sin 4\beta$. At $\gamma = \pi/2$ and $\beta = -\pi/8$ this is $-1$: probability $\frac12$ on $|01\rangle$ and $\frac12$ on $|10\rangle$, both cut states. The sign matters: change $\beta$ to $+\pi/8$ and you get $+1$, the worst coloring.

## How good is a given state?

The **approximation ratio** is the expected cut divided by the best cut. If a state has $\langle H_C\rangle = -2.6$, the expected cut is $(6+2.6)/2 = 4.3$ and the ratio is $4.3/5 = 0.86$. The optimum, $\langle H_C\rangle = -4$, has expected cut $5$ and ratio $1$. The mission asks for more than $0.85$.

Training the angles from 25 random starting points on this graph gives the best ratios 0.822 for $p = 1$, 0.925 for $p = 2$ and 0.965 for $p = 3$. One layer cannot reach 0.85 here. There is a general reason one layer falls short: after $p$ layers, the expectation $\langle Z_iZ_j\rangle$ of an edge depends only on the part of the graph within $p$ edges of that edge, and all edges share the same two angles. One layer tunes every edge from its immediate neighbourhood only, and it has no way to let a choice on one edge depend on a conflict at the other end of the graph. Each added layer reaches one edge further and adds two angles. Setting the new angles to zero reproduces the previous circuit, so the best ratio can never decrease with $p$.
