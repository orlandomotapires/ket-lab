## A hidden collision pattern

A function $f:\{0,1\}^3 \to \{0,1\}^3$ is given as an oracle, with a promise: for some secret string $s$,

$$
f(x) = f(y) \iff y = x \ \text{ or } \ y = x \oplus s
$$

where $\oplus$ is bitwise XOR. For $s = 110$ this means $f(000) = f(110)$, $f(001) = f(111)$ and so on: the inputs pair up as $\{x, x\oplus s\}$ and every pair has its own output. For $s = 000$ the condition says $f$ is one-to-one, so $s = 000$ is a valid answer and means "no collisions". The task is to find $s$.

Classically $s$ shows up only through a collision $f(x) = f(y)$ with $x \neq y$, because then $s = x \oplus y$. With $q$ queries there are about $q^2/2$ pairs, so a collision takes $q = \Theta(2^{n/2})$ queries even with randomization. Simon's algorithm needs $O(n)$.

## The circuit, with $n = 2$ first

Use $n$ input qubits and $n$ output qubits, all in $|0\rangle$, and the query $U_f|x\rangle|z\rangle = |x\rangle|z \oplus f(x)\rangle$. Apply $H^{\otimes n}$ to the input, query once, apply $H^{\otimes n}$ to the input again and measure it.

Take $n = 2$, $s = 11$, with $f(00) = f(11) = 0$ and $f(01) = f(10) = 1$ (the output has one bit that matters). After the first Hadamards and the query the state is

$$
\tfrac12\big[(|00\rangle + |11\rangle)|0\rangle + (|01\rangle + |10\rangle)|1\rangle\big]
$$

The second Hadamard layer turns $(|00\rangle + |11\rangle)/\sqrt2$ into itself, and $(|01\rangle + |10\rangle)/\sqrt2$ into $(|00\rangle - |11\rangle)/\sqrt2$. Either way the input measures to $00$ or $11$, each with probability $1/2$, and never to $01$ or $10$. Both outcomes satisfy $y \cdot s = 0 \pmod 2$. The outcome $11$ is one equation, $s_0 \oplus s_1 = 0$, which already leaves a single nonzero solution, $s = 11$.

In general, group the terms of the state by output value. For $s \neq 0^n$ each value $f(x)$ comes from exactly $x$ and $x \oplus s$, giving $\frac{|x\rangle + |x\oplus s\rangle}{\sqrt2}$ on the input. Since $H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}}\sum_y (-1)^{x\cdot y}|y\rangle$,

$$
H^{\otimes n}\frac{|x\rangle + |x\oplus s\rangle}{\sqrt2} = \frac{1}{\sqrt{2^{n+1}}}\sum_y (-1)^{x\cdot y}\left(1 + (-1)^{s\cdot y}\right)|y\rangle
$$

The factor $1 + (-1)^{s\cdot y}$ is 2 when $s\cdot y = 0 \pmod 2$ and 0 otherwise. Each run returns a string $y$ drawn uniformly from the $2^{n-1}$ strings with $y\cdot s = 0$. For $s = 0^n$ the factor is always 2 and the outcome is uniform over all $2^n$ strings.

## Solving for $s$

Each outcome is a linear equation $y\cdot s = 0$ over the field with two elements. One equation leaves a solution space of dimension $n-1$, and every independent outcome removes one dimension, so $n-1$ independent outcomes leave exactly one nonzero solution, which is $s$. A new random outcome is independent of the earlier ones with probability at least $1/2$, so $O(n)$ runs are enough with high probability. Gaussian elimination modulo 2 does the algebra in $O(n^3)$ steps; for $n=3$ you can test the 7 nonzero candidates against every outcome.

If $s \neq 0^n$, $s$ satisfies every equation and always survives. If no nonzero candidate survives, $s = 0^n$. When $s = 0^n$ and you have few outcomes, a nonzero candidate may survive by luck, so collect enough of them. Qubit 0 is the last character of every string, so $s = s_2s_1s_0$ and an outcome is $y_2y_1y_0$; the inner product $y\cdot s$ does not depend on the order if both strings use the same one.

For $n=3$ and $s \neq 000$, the histogram of the input register shows four strings with probability $1/4$ each. Predict which four before you look.
