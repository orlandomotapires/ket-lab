## Factoring as period finding

Shor's algorithm factors a composite number $N$ by finding the **period** (the order) of

$$
f(x) = a^x \bmod N
$$

for an integer $a$ coprime to $N$. The period $r$ is the smallest positive integer with $a^r \equiv 1 \pmod N$. This task is called **order finding**.

For $N = 15$ and $a = 7$, the sequence $7^x \bmod 15$ is $1, 7, 4, 13, 1, 7, 4, 13, \dots$ and $r = 4$.

## From the period to the factors

If $r$ is even, then $a^r - 1 = (a^{r/2} - 1)(a^{r/2} + 1)$ is a multiple of $N$. Unless one of the two factors is itself a multiple of $N$, each shares a nontrivial divisor with $N$:

$$
\gcd(a^{r/2} - 1,\, N) \qquad \text{and} \qquad \gcd(a^{r/2} + 1,\, N)
$$

For $r = 4$: $7^2 = 49$, $\gcd(48, 15) = 3$ and $\gcd(50, 15) = 5$.

## The quantum part

The map $U|y\rangle = |7y \bmod 15\rangle$ is unitary. Its eigenvalues are $e^{2\pi i\,s/r}$ with $s = 0, \dots, r-1$, and the state $|1\rangle$ is an equal superposition of the corresponding eigenvectors. Phase estimation applied to $U$ with the work register in $|1\rangle$ therefore measures $s/r$ for a value of $s$ chosen uniformly at random.

With 4 counting qubits, $s/4$ is a multiple of $1/16$, and the possible results are $m = 16\,s/4 = 0, 4, 8, 12$, each with probability $1/4$.

## Classical post-processing

A result $m$ gives the estimate $m/16$ of $s/r$. The fraction with the smallest denominator close to it gives $r$:

```python
from fractions import Fraction
Fraction(12, 16).limit_denominator(15)   # 3/4, so r = 4
```

Some results do not give $r$. For $m = 0$ the fraction is $0$ and $r = 1$ is wrong. For $m = 8$ the fraction is $1/2$, which gives $r = 2$, but $7^2 \bmod 15 = 4 \neq 1$. This happens when $s/r$ is not in lowest terms: here $s = 2$, and the denominator found is $r/\gcd(s, r)$. So check `pow(a, r, N) == 1` before using $r$, and combine several measurements.

## Choosing $a$ and when a run fails

Choose $a$ at random with $1 < a < N$. If $\gcd(a, N) \neq 1$, that gcd is already a factor. Otherwise a run fails when:

- $r$ is odd, so $a^{r/2}$ is not an integer;
- $a^{r/2} \equiv -1 \pmod N$, so $a^{r/2} + 1$ is a multiple of $N$ and the gcds are $1$ and $N$. For example $a = 14 \equiv -1 \pmod{15}$ has $r = 2$ and $14^1 \equiv -1$.

For $N$ with at least two distinct odd prime factors, a random $a$ succeeds with probability at least $1/2$. After a failure, choose another $a$.

## Continued fractions

The result $m$ approximates $s/r$ by $m/2^t$. To recover $r$, expand $m/2^t$ as a continued fraction and take the convergent with denominator at most $N$, which is what `limit_denominator(N)` does. Correctness is guaranteed when $2^t \ge N^2$, which needs $t = 8$ counting qubits for $N = 15$. With $t = 4$ it still works here, because $s/4$ is exactly a multiple of $1/16$ and the estimates are exact.

## In the lab

- `apply_controlled_mod_mult(qc, control, power)` multiplies the work register (qubits 4 to 7) by $7^{\text{power}} \bmod 15$, controlled by qubit `control`.
- `inverse_qft(qc, qubits)` applies the inverse QFT.
- `run_shots(qc)` runs the circuit 1024 times and returns the counts.

The Period tab shows $7^x \bmod 15$. The Register tab shows the peaks of the counting register.
