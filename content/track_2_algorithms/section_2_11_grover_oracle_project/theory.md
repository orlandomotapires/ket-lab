## An oracle is a piece of engineering

In lesson 2.6 the oracle was handed to you. In practice Grover's algorithm is only as useful as the oracle someone can write for it, and that is where the work is. Checking a candidate is usually cheap; making that check a unitary that flips a sign is the task.

Here the problem is small enough to follow by hand. Three Boolean variables $a, b, c$ (qubits 0, 1, 2) must satisfy

$$
f(a,b,c) = (a \lor b) \land (\lnot a \lor c) \land (\lnot b \lor \lnot c).
$$

Evaluate $f$ on the eight assignments on paper first. The number of assignments that pass is the $M$ of the search, and you need it to choose the number of iterations. A result is printed as the string $c\,b\,a$, because qubit 0 is the rightmost character.

## Two ways to build the oracle

The phase oracle should satisfy $U_f|x\rangle|0\rangle_{\text{anc}} = (-1)^{f(x)}|x\rangle|0\rangle_{\text{anc}}$; qubits 3 and 4 are optional ancillas that must end in $|0\rangle$.

One way marks each solution directly: put $X$ gates on the qubits that are 0 in that string, then a Z controlled by all three, then the same $X$ gates again. The other way computes each clause into an ancilla, marks the state where every clause holds, and undoes the computation. It is longer here, but it is the method that scales to larger formulas.

Undoing the ancillas matters. If an ancilla keeps a record of the clauses, it is entangled with the search register, and amplitudes that should add up no longer do.

## Iterations and a way to test

With $N = 8$ and $M$ solutions, $\sin\theta = \sqrt{M/N}$ and the probability after $k$ iterations is $\sin^2((2k+1)\theta)$, as in lesson 2.6. For your $M$, find the $k$ that brings $(2k+1)\theta$ closest to $90°$, and remember that going past it makes things worse.

You can test the oracle alone before you build the search: apply it to each basis state and see which ones change sign. Searching $n$ variables still costs about $2^{n/2}$ queries, so a formula with many variables stays hard.
