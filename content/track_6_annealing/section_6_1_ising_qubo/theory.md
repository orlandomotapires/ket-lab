## Splitting five numbers

Can you split the numbers 4, 5, 6, 7, 8 into two groups with the same sum? They add up to 30, so each group needs 15, and $\{7, 8\}$ against $\{4, 5, 6\}$ works. Give every number a spin $s_i = +1$ if it goes in the first group and $s_i = -1$ if it goes in the second. Then $\sum_i a_i s_i$ is the difference of the two sums, and the cost

$$
E(s) = \Big(\sum_i a_i s_i\Big)^2
$$

is zero exactly for a perfect split. A problem written as "find the spins of lowest energy" is what a quantum annealer takes as input, and the rest of the track builds on this form.

## Expanding the square

Expanding gives $\sum_i a_i^2 s_i^2 + 2\sum_{i<j} a_i a_j s_i s_j$. Since $s_i^2 = 1$, the first sum is the constant $\sum_i a_i^2 = 190$. What remains is an **Ising energy** with couplings $J_{ij} = 2 a_i a_j$ for $i < j$ and no fields:

$$
E(s) = \sum_{i<j} J_{ij}\, s_i s_j + 190, \qquad J_{01} = 2\cdot4\cdot5 = 40, \quad J_{34} = 2\cdot7\cdot8 = 112.
$$

The constant does not change which state is lowest. We keep it so that the energy is the cost itself and the best value is 0. All couplings are positive, so a pair of spins lowers the energy by pointing in opposite directions. The factor 2 is the usual slip: each pair appears twice in the square.

Because every term holds a product of two spins, flipping all spins leaves $E$ unchanged. Each solution is found twice, as $s$ and $-s$. This is a property of any model without fields, and it will matter when we remove it.

## Brute force

With five spins there are $2^5 = 32$ states, and you can list them all. In the order of `itertools.product([1, -1], repeat=5)` the first is $(+1, +1, +1, +1, +1)$ with energy $30^2 = 900$. The state $(+1, +1, +1, -1, -1)$ has $4 + 5 + 6 - 7 - 8 = 0$, and so does its mirror image. They are the only two ground states: the next energy is 4, reached by two states. Enumeration costs $2^N$, which is fine for $N = 5$ and hopeless for $N = 100$. Finding the ground state of an Ising model is hard in general, and that is why annealing is tried on it as a heuristic, with no guarantee.

## From spins to bits: the QUBO form

Many solvers take bits $x_i \in \{0, 1\}$ instead. With $s = 1 - 2x$, the spin $+1$ is the bit 0, which is the state $|0\rangle$ and the $+1$ eigenvalue of $Z$. A **QUBO** (quadratic unconstrained binary optimization) is $E(x) = x^\top Q x + \text{offset}$ with $Q$ upper triangular. Do two numbers by hand, $a = (1, 2)$:

$$
E = (s_0 + 2 s_1)^2 = 5 + 4 s_0 s_1, \qquad s_0 s_1 = (1-2x_0)(1-2x_1) = 1 - 2x_0 - 2x_1 + 4x_0 x_1,
$$

so $E = 9 - 8x_0 - 8x_1 + 16 x_0 x_1$. The linear terms go on the diagonal because $x^2 = x$: $Q = \begin{pmatrix} -8 & 16 \\ 0 & -8 \end{pmatrix}$ and the offset is 9. Check $x = (1, 0)$: $s = (-1, +1)$, $(-1 + 2)^2 = 1$, and $9 - 8 = 1$. In general, with $S = \sum a_i$,

$$
Q_{ii} = 4 a_i (a_i - S), \qquad Q_{ij} = 8 a_i a_j \ (i<j), \qquad \text{offset} = S^2.
$$

For our set, $S = 30$, $Q_{00} = -416$, $Q_{01} = 160$, offset 900. Without fields the change $x = (1+s)/2$ would give the same $Q$, because $E(s) = E(-s)$. With fields the signs of the linear terms depend on the convention, so this track always uses $x = (1-s)/2$.

## Max-Cut on a triangle

Max-Cut, treated with QAOA in lesson 3.3, has the same form. Put a spin on each vertex and a coupling $J = +1$ on each edge, $E = \sum_{\text{edges}} s_i s_j$. A cut edge has $s_i s_j = -1$, so $E = 3 - 2\cdot(\text{cut edges})$ on a triangle. Three edges cannot all be cut: among three $\pm1$ spins two agree. The best energy is $-1$ (two edges cut), reached by 6 of the 8 states. No state satisfies every coupling, which is called **frustration**.

## Removing the symmetry

Take $\{1, 2, 3, 4\}$ and fix the 4 on the $+$ side, which leaves three spins for the numbers 1, 2, 3:

$$
(4 + s_0 + 2s_1 + 3s_2)^2 = 30 + 8s_0 + 16s_1 + 24s_2 + 4s_0s_1 + 6s_0s_2 + 12s_1s_2.
$$

The cross terms with the fixed spin are linear in the others, so **fields** appear. Dividing by 24, $h = (\tfrac13, \tfrac23, 1)$, $J_{01} = \tfrac16$, $J_{02} = \tfrac14$, $J_{12} = \tfrac12$, constant $\tfrac54$. The unique ground state is $s = (+1, -1, -1)$, energy $-\tfrac54$ (cost 0): the 1 joins the 4, and 2 and 3 form the other side. In Qiskit's order this is the basis state $|110\rangle$. This three-qubit instance is the one the next lessons anneal.
