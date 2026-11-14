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

Not every result works: $m = 0$ tells you nothing, and $m = 8$ gives $r = 2$, which reveals only the factor $3$. That is why the algorithm combines several measurements.

## In the lab

- `apply_controlled_mod_mult(qc, control, power)` multiplies the work register (qubits 4 to 7) by $7^{\text{power}} \bmod 15$, controlled by the given qubit.
- `inverse_qft(qc, qubits)` is the inverse QFT.
- `run_shots(qc)` runs the circuit 1024 times and returns the counts.

The **Period** tab shows $7^x \bmod 15$; the **Register** tab shows the peaks of the counting register.
