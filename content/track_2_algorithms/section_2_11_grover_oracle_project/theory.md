## What to build

This project assembles the whole of Grover's algorithm for a small constraint problem. Three Boolean variables $a, b, c$ (qubits 0, 1, 2) must satisfy

$$
f(a,b,c) = (a \lor b) \land (\lnot a \lor c) \land (\lnot b \lor \lnot c).
$$

You write the oracle yourself. It is the phase oracle of lesson 2.6,

$$
U_f|x\rangle|0\rangle_{\text{anc}} = (-1)^{f(x)}|x\rangle|0\rangle_{\text{anc}},
$$

where qubits 3 and 4 are optional ancillas. Two routes work:

- Mark each satisfying string directly: $X$ gates on its zero bits, a controlled-controlled-$Z$, the same $X$ gates again.
- Compute each clause into an ancilla, mark the state where all clauses hold, then uncompute the ancillas. This scales to larger formulas.

A result is written as the bit string $|c\,b\,a\rangle$, since qubit 0 is the rightmost character (Qiskit ordering).

## Number of iterations

With $N = 2^3 = 8$ candidates and $M$ solutions, $\sin\theta = \sqrt{M/N}$ and the success probability after $k$ iterations is $\sin^2((2k+1)\theta)$. Use $k = \lfloor \frac{\pi}{4}\sqrt{N/M} \rfloor$. For this formula $M$ is the number of satisfying strings you found by hand.

## Rubric

The validator checks five independent criteria and reports the first that fails.

1. `oracle(qc)` exists and builds a unitary circuit on at most 5 qubits.
2. Alone, the oracle multiplies each basis state by $-1$ if it satisfies $f$ and by $+1$ otherwise, and returns the ancillas to $|0\rangle$. The validator checks this on all 8 inputs.
3. `iterations` is the optimal count for $N = 8$ and $M = 2$.
4. The probability that `qc` yields a solution is at least $0.95$ (computed from the state vector before the measurements).
5. `solutions` contains exactly the strings found with `run_shots`.

## Limits

Searching $n$ variables takes about $2^{n/2}$ oracle queries, so a formula with many variables stays hard even though the speedup is quadratic.
