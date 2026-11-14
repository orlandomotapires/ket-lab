## Qubits on a lattice

The **toric code** places one qubit on each edge of an $L \times L$ square lattice with periodic boundaries (a torus). There are $2L^2$ qubits: $L^2$ horizontal and $L^2$ vertical edges. Index the vertices by $(r, c)$ with $r, c$ taken modulo $L$. The horizontal edge $h(r,c)$ joins $(r,c)$ to $(r,c+1)$, and the vertical edge $v(r,c)$ joins $(r,c)$ to $(r+1,c)$.

There are two kinds of stabilizer generators:

- **Star** $A_s$ at vertex $s=(r,c)$: $X$ on the four edges that touch the vertex, $h(r,c),\ h(r,c-1),\ v(r,c),\ v(r-1,c)$.
- **Plaquette** $B_p$ for the square $p=(r,c)$ with corners $(r,c), (r,c+1), (r+1,c), (r+1,c+1)$: $Z$ on its four edges, $h(r,c),\ h(r+1,c),\ v(r,c),\ v(r,c+1)$.

A star and a plaquette share either no edge or two edges, so they commute (two positions where $X$ meets $Z$). Stars commute among themselves, and so do plaquettes. All $2L^2$ qubits are constrained by $2L^2$ generators, but the product of all stars is the identity and so is the product of all plaquettes. Only $2L^2 - 2$ generators are independent, so the code space has dimension $2^2$: the toric code encodes $k = 2$ qubits.

## Errors are strings, defects are endpoints

An $X$ error on an edge anticommutes with the plaquettes that contain it. Every edge borders two plaquettes, so one $X$ error lights up two plaquettes. For a chain of $X$ errors on several edges, a plaquette lights up when it contains an odd number of them. Two errors on neighbouring edges that share a plaquette cancel there, and the defects stay only at the two ends of the chain. A **defect** is a stabilizer with eigenvalue $-1$.

The same holds for $Z$ errors and stars. The syndrome is the set of defects, and a decoder must pair them up and guess the chains that connect each pair.

## Loops

A chain with no endpoints (a closed loop) has an empty syndrome. There are two cases:

- A contractible loop is a product of stars (for $X$ errors), so it fixes the code space: acting with it changes nothing.
- A loop that wraps around the torus is not a product of stars. It commutes with every generator and changes the encoded state, so it is a logical operator.

To tell them apart, count how many edges of the chain lie on a fixed $Z$-loop. The row $\prod_c Z_{h(0,c)}$ and the column $\prod_r Z_{v(r,0)}$ are two such loops. They commute with all stars (each star touches a loop in 0 or 2 edges) and are not products of plaquettes. An $X$ chain without defects anticommutes with the row when it has an odd number of edges in it, and likewise for the column. The pair of parities $(a, b)$ is $(0,0)$ for a trivial loop and different from $(0,0)$ for a logical operator. For example, $X$ on every $v(r_0, c)$ in one row gives $(0,1)$, and $X$ on every $h(r,c_0)$ in one column gives $(1,0)$.

## Distance

A logical operator must wrap around the torus, so it has at least $L$ edges, and a loop of $L$ edges exists. Any error with fewer than $L$ edges is therefore either detected or a product of stabilizers. The code distance is $d = L$, and the code parameters are $[[2L^2,\, 2,\, L]]$.

Increasing $L$ raises the distance, but the number of qubits grows as $L^2$. In the exercise you find $d$ for $L=3$ by brute force: no chain with fewer than 3 edges is an undetected logical operator, and some chain with 3 edges is.
