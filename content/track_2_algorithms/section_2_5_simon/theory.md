## The problem

A function $f:\{0,1\}^n \to \{0,1\}^n$ is given as an oracle, with the promise that for some string $s \in \{0,1\}^n$

$$
f(x) = f(y) \iff y = x \ \text{ or } \ y = x \oplus s
$$

where $\oplus$ is the bitwise XOR. The task is to find $s$.

If $s \neq 0^n$, then $f$ is two-to-one: the inputs pair up as $\{x, x\oplus s\}$ and each pair has its own output. If $s = 0^n$, the condition reads $f(x)=f(y) \iff y = x$, so $f$ is one-to-one. The string $s = 000$ is therefore a valid answer: it means that $f$ has no collisions.

Classically, $s$ is revealed only by a collision $f(x)=f(y)$ with $x\neq y$, since then $s = x\oplus y$. Among $q$ distinct queries there are about $q^2/2$ pairs, so a collision needs $q = \Theta(2^{n/2})$ queries, even with randomization. Simon's algorithm needs $O(n)$ queries, an exponential separation in query complexity.

## The circuit

Use an input register of $n$ qubits and an output register of $n$ qubits, all in $|0\rangle$, and the query gate $U_f|x\rangle|z\rangle = |x\rangle|z\oplus f(x)\rangle$.

1. Apply $H^{\otimes n}$ to the input register: $\frac{1}{\sqrt{2^n}}\sum_x |x\rangle|0^n\rangle$.
2. Apply $U_f$: $\frac{1}{\sqrt{2^n}}\sum_x |x\rangle|f(x)\rangle$.
3. Apply $H^{\otimes n}$ to the input register and measure it.

Group the terms by output value. For $s \neq 0^n$, each value $f(x)$ appears for exactly $x$ and $x\oplus s$, so the state is $\frac{1}{\sqrt{2^{n-1}}}\sum_{x \in A}\frac{|x\rangle + |x\oplus s\rangle}{\sqrt2}|f(x)\rangle$, where $A$ contains one input from each pair. A Hadamard layer maps $|x\rangle$ to $\frac{1}{\sqrt{2^n}}\sum_y (-1)^{x\cdot y}|y\rangle$, hence

$$
H^{\otimes n}\frac{|x\rangle + |x\oplus s\rangle}{\sqrt2} = \frac{1}{\sqrt{2^{n+1}}}\sum_y (-1)^{x\cdot y}\left(1 + (-1)^{s\cdot y}\right)|y\rangle.
$$

The factor $1+(-1)^{s\cdot y}$ is 2 when $s\cdot y = 0 \pmod 2$ and 0 otherwise. Each measurement of the input register returns a string $y$ chosen uniformly from the $2^{n-1}$ strings with

$$
y \cdot s = y_0 s_0 \oplus \dots \oplus y_{n-1}s_{n-1} = 0 \pmod 2
$$

For $s = 0^n$ the factor is always 2 and the outcome is uniform over all $2^n$ strings, which is consistent with the same equation.

## Classical post-processing

Each outcome $y$ is one linear equation $y\cdot s = 0$ over the field with two elements. The solutions of one equation form a subspace of dimension $n-1$. Outcomes that are linearly independent (modulo 2) cut the dimension of the solution space by one each, so $n-1$ independent outcomes leave exactly one nonzero solution, which is $s$.

A random outcome is independent of the previous ones with probability at least $1/2$, so $O(n)$ runs give $n-1$ independent equations with high probability. Gaussian elimination modulo 2 solves the system in $O(n^3)$ steps. For $n=3$ the system is small enough to test each of the 7 nonzero candidates against every outcome.

If $s\neq 0^n$, the string $s$ satisfies every equation, so it is always among the solutions. If no nonzero string satisfies all the equations, then $s=0^n$ with certainty. In the other direction, a nonzero candidate that survives may be spurious when $s=0^n$ and few outcomes were collected: the outcomes are uniform over all strings and, with enough of them, span $\{0,1\}^n$ and eliminate every nonzero candidate.

## In the lab

The oracle is a single gate on 6 qubits. Before the second Hadamard layer, the input register is in a superposition that depends on $s$. In the histogram, the measured strings are those orthogonal to $s$, each with probability $1/4$ for $n=3$ and $s\neq 000$. Validation runs your code with eight hidden strings, including $000$, and compares `s_found` with each.

## Qubit ordering

Nielsen & Chuang write qubit 0 on the left of the label. Qiskit, and this lab, write qubit 0 on the right, so $s = s_2s_1s_0$ and an outcome is $y_2y_1y_0$. The inner product $y\cdot s$ does not depend on the order as long as both strings use the same one.
