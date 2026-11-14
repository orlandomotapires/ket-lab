## Factoring is finding a period

The security of RSA cryptography depends on large numbers being hard to factor. Shor showed that factoring a composite number $N$ reduces to finding the **period** of the function

$$
f(x) = a^x \bmod N
$$

for a randomly chosen $a$ with no common divisors with $N$. The period $r$ is the smallest positive integer with $a^r \bmod N = 1$.

With $N = 15$ and $a = 7$, the sequence $7^x \bmod 15$ is $1, 7, 4, 13, 1, 7, 4, 13, \dots$ and the period is $r = 4$.

## From the period to the factors

If $r$ is even, $a^r - 1 = (a^{r/2} - 1)(a^{r/2} + 1)$ is a multiple of $N$, and each of the two factors shares a divisor with $N$:

$$
\text{gcd}(a^{r/2} - 1,\, N) \qquad \text{and} \qquad \text{gcd}(a^{r/2} + 1,\, N)
$$

With $r = 4$: $7^2 = 49$, $\text{gcd}(48, 15) = 3$ and $\text{gcd}(50, 15) = 5$.

## The quantum part

The modular multiplication $U|y\rangle = |7y \bmod 15\rangle$ is a unitary operation, with eigenvalues $e^{2\pi i\,s/r}$. Starting the work register in $|1\rangle$ and applying the phase estimation from the previous lesson, the counting register measures $s/r$ for an $s$ drawn between $0$ and $r - 1$. With 4 counting qubits, the possible results are $16 \cdot s/4 = 0,\ 4,\ 8,\ 12$.

## Classical post-processing

For each result $m$, the phase is $m/16$. The nearest fraction with a small denominator reveals $r$:

```python
from fractions import Fraction
Fraction(12 / 16).limit_denominator(15)   # 3/4, so r = 4
```

Not every result works: $m = 0$ tells you nothing, and $m = 8$ gives $r = 2$, which is not the period (check: $7^2 \bmod 15 = 4 \neq 1$). That is why the check `pow(a, r, N) == 1` comes before using $r$, and why the algorithm combines several measurements.

## How to choose $a$ and when it fails

Pick $a$ at random with $1 < a < N$. If $\text{gcd}(a, N) \neq 1$, the gcd is already a factor and no quantum step is needed. Otherwise, an attempt fails when:

- $r$ is **odd**: $a^r - 1$ cannot be split into two factors;
- $a^{r/2} \equiv -1 \pmod N$: then $a^{r/2} + 1$ is a multiple of $N$ and the two gcds are $1$ and $N$. Example: $a = 14 \equiv -1 \pmod{15}$ has $r = 2$ and $14^1 \equiv -1$, so nothing is learned.

For a randomly drawn $a$, each run succeeds with probability above 50%; if it fails, draw another $a$ and repeat.

## The continued-fraction step

The result $m$ approximates $s/r$ by $m/2^t$. To recover $r$, take the continued-fraction expansion of $m/2^t$ and pick the convergent with denominator at most $N$. That is what `limit_denominator(N)` does. With $2^t \geq N^2$ the right convergent is guaranteed (that needs $t = 8$ counting qubits for $N = 15$); here, with $N = 15$ and 4 qubits, the problem is small enough to work anyway.

## In the lab

- `apply_controlled_mod_mult(qc, control, power)` multiplies the work register (qubits 4 to 7) by $7^{\text{power}} \bmod 15$, controlled by the given qubit.
- `inverse_qft(qc, qubits)` is the inverse QFT.
- `run_shots(qc)` runs the circuit 1024 times and returns the counts.

The **Period** tab shows $7^x \bmod 15$; the **Register** tab shows the peaks of the counting register.
