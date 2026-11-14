## The Max-Cut problem

Given a graph, split the vertices into two groups so that as many edges as possible connect vertices in different groups ("cut" edges). It is an NP-hard problem: for large graphs, no efficient algorithm is known that guarantees the optimum. It appears in circuit design, data clustering and statistical physics.

In this graph of 5 vertices and 6 edges, the best cut is 5.

## From the graph to the qubits

Each vertex becomes a qubit: $|0\rangle$ and $|1\rangle$ indicate the group. An edge $(i, j)$ is cut when the bits differ, that is, when $Z_i Z_j = -1$. Then

$$
\text{cut} = \sum_{(i,j)} \frac{1 - Z_i Z_j}{2}
$$

and maximizing the cut is the same as **minimizing** the Ising energy $H_C = \sum_{(i,j)} Z_i Z_j$. In the lab, `cost_h` is this $H_C$.

## The QAOA

The *Quantum Approximate Optimization Algorithm* alternates two kinds of layer, starting from the uniform superposition:

$$
|\vec\gamma, \vec\beta\rangle = U_M(\beta_p)\,U_C(\gamma_p) \cdots U_M(\beta_1)\,U_C(\gamma_1)\,|+\rangle^{\otimes n}
$$

- **Cost**, $U_C(\gamma) = e^{-i\gamma H_C/2}$: an `IsingZZ(γ)` on each edge. It imprints on the amplitudes a phase that depends on the cut.
- **Mixer**, $U_M(\beta) = e^{-i\beta \sum X}$: an `RX(2β)` on each qubit. It turns these phases into changes in probability, through interference.

A classical optimizer adjusts the $2p$ angles to minimize $\langle H_C \rangle$. It is the same hybrid loop as in the previous lessons.

## The approximation ratio

The result is measured by the **approximation ratio**: the expected cut of the final state divided by the maximum cut. A ratio of 1 would mean always measuring the optimal solution. The larger $p$ is, the closer to 1 QAOA can get; as $p \to \infty$, it recovers quantum annealing.

## In the lab

- The **Graph** tab shows the vertices colored by the most likely cut, with the cut edges highlighted, and the approximation ratio.
- The **Convergence** tab shows the ratio at each step, with the threshold of 0.85.
- The **Register** tab shows the probability of each of the 32 partitions.

The starter code uses a single layer. Click **Run** (or Ctrl+Enter) to train.
