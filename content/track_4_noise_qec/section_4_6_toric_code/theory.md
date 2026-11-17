## Two errors that nearly cancel

Put one $X$ error on an edge of a lattice of qubits and a check next to it fires. Put a second $X$ on the neighbouring edge, and one of the two firing checks goes quiet again, leaving a pair of checks at the far ends. Errors on a lattice behave like strings, and the checks that fire are the string's endpoints. That is the picture behind the **toric code**, and the rest of the lesson makes it exact.

The code places one qubit on each edge of an $L\times L$ square lattice with periodic boundaries, a torus, so there are $2L^2$ qubits: $L^2$ horizontal and $L^2$ vertical edges (18 for $L=3$). Vertices are labelled $(r,c)$ modulo $L$. The horizontal edge $h(r,c)$ joins $(r,c)$ to $(r,c+1)$, and the vertical edge $v(r,c)$ joins $(r,c)$ to $(r+1,c)$.

## Stars, plaquettes and how many qubits they encode

The checks are of two kinds. The **star** $A_s$ at vertex $s=(r,c)$ is $X$ on the four edges that touch the vertex: $h(r,c),\ h(r,c-1),\ v(r,c),\ v(r-1,c)$. The **plaquette** $B_p$ of the square with corners $(r,c),(r,c+1),(r+1,c),(r+1,c+1)$ is $Z$ on its four edges: $h(r,c),\ h(r+1,c),\ v(r,c),\ v(r,c+1)$.

A star and a plaquette share no edge or two edges, so $X$ meets $Z$ at an even number of positions and they commute (lesson 4.5). Stars commute with each other, and so do plaquettes. There are $2L^2$ generators for $2L^2$ qubits, but the product of all stars is the identity, and so is the product of all plaquettes, so only $2L^2-2$ are independent. The code space has dimension $2^{2L^2-(2L^2-2)}=2^2$: the toric code encodes $k=2$ qubits, whatever $L$ is.

## Chains and their endpoints

An $X$ error on an edge anticommutes with the plaquettes that contain it, and every edge lies in two plaquettes, so one error lights two. A defect is a stabilizer with eigenvalue $-1$. For a chain of several $X$ errors, a plaquette lights up when it holds an odd number of them. On $L=3$, errors on $v(0,1)$ and $v(0,2)$ share the plaquette $(0,1)$, which holds two errors and stays quiet, and the defects are at $(0,0)$ and $(0,2)$. The same holds for $Z$ errors and stars. The syndrome is the set of defects, and a decoder has to pair them up and guess the chains that join each pair.

## Loops: harmless and harmful

A chain with no endpoints, a closed loop, has an empty syndrome, and two things can be true of it. A loop that can be shrunk to nothing is a product of stars, which fixes the code space, so it does nothing. A loop that wraps around the torus is not a product of stars. It commutes with every generator and changes the encoded state: a logical operator.

To tell them apart, count the edges of the chain that lie on a fixed $Z$-loop: the row $\prod_c Z_{h(0,c)}$ or the column $\prod_r Z_{v(r,0)}$. Both commute with all stars and are not products of plaquettes. A defect-free $X$ chain anticommutes with the row when it has an odd number of edges in it, and likewise for the column. The two parities $(a,b)$ are $(0,0)$ for a trivial loop. For $X$ on every $v(r_0,c)$ in one row they are $(0,1)$ (the chain meets the column $v(r,0)$ once), and for $X$ on every $h(r,c_0)$ in one column they are $(1,0)$.

## Distance

A logical operator has to wrap around the torus, so it has at least $L$ edges, and a loop of exactly $L$ edges exists. Any error with fewer than $L$ edges is therefore either seen by some check or a product of stabilizers, and the distance is $d=L$. The parameters are $[[2L^2,2,L]]$: 18 qubits and distance 3 for $L=3$, 32 qubits and distance 4 for $L=4$. Raising the distance costs qubits quadratically, since doubling $L$ quadruples them. In the exercise you find $d$ for $L=3$ by brute force, going through chains by size.
