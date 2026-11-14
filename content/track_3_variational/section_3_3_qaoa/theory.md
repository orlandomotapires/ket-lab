## The Max-Cut problem

Given a graph, divide the vertices into two groups so that as many edges as possible join vertices in different groups. Those edges are **cut**. Max-Cut is NP-hard, so no efficient exact algorithm is known for large graphs.

The graph in this lesson has 5 vertices and 6 edges. It contains the triangle 0–1–4, and no two-group split can cut all three of its edges, so the maximum cut is 5.

## From the graph to qubits

Each vertex is a qubit, and $|0\rangle$ or $|1\rangle$ gives its group. Edge $(i,j)$ is cut when the two bits differ, that is, when $Z_iZ_j = -1$. The cut size is therefore

$$
\text{cut} = \sum_{(i,j)} \frac{1 - Z_i Z_j}{2}
$$

Maximizing it is the same as minimizing the Ising energy $H_C = \sum_{(i,j)} Z_i Z_j$, the **cost Hamiltonian**. In the lab, `cost_h` is $H_C$. For a state with $\langle H_C\rangle = E$, the expected cut is $(6 - E)/2$ on this graph.

## The QAOA

The **quantum approximate optimization algorithm** starts from the uniform superposition and applies $p$ layers, each made of a cost unitary and a mixer unitary:

$$
|\vec\gamma, \vec\beta\rangle = U_M(\beta_p)\,U_C(\gamma_p) \cdots U_M(\beta_1)\,U_C(\gamma_1)\,|+\rangle^{\otimes n}
$$

- Cost unitary: $U_C(\gamma) = e^{-i\gamma H_C/2}$, an `IsingZZ(γ)` on each edge. It gives each basis state a phase that depends on its cut size.
- Mixer unitary: $U_M(\beta) = e^{-i\beta \sum_k X_k}$, an `RX(2β)` on each qubit. The mixer Hamiltonian $\sum_k X_k$ turns the phase differences into differences in probability.

A classical optimizer adjusts the $2p$ angles to minimize $\langle H_C\rangle$, the same hybrid loop as in lesson 3.1.

## The approximation ratio

The **approximation ratio** is the expected cut of the final state divided by the maximum cut. A ratio of 1 means every measurement returns an optimal cut. Increasing $p$ cannot lower the best achievable ratio, and as $p\to\infty$ the ratio tends to 1.

For this graph, the best ratio at $p=1$ is about 0.82, and at $p=2$ it is about 0.92.

## In the lab

- Graph: the vertices colored by the most likely cut, the cut edges, and the approximation ratio.
- Convergence: the ratio at each step, with the threshold 0.85.
- Register: the probability of each of the 32 partitions.

The starter code uses one layer. Click Run (or press Ctrl+Enter) to train.
