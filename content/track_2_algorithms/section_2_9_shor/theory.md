## Factoring as period finding

Factoring 15 by hand is easy. For a number with hundreds of digits no fast classical method is known. Shor's algorithm reduces factoring to finding the **period** of $f(x) = a^x \bmod N$ for some $a$ coprime to $N$: the smallest $r > 0$ with $a^r \equiv 1 \pmod N$, also called the order of $a$. For $N = 15$ and $a = 7$ the sequence $7^x \bmod 15$ is $1, 7, 4, 13, 1, 7, 4, 13, \dots$ and $r = 4$.

## From the period to the factors

If $r$ is even, $a^r - 1 = (a^{r/2} - 1)(a^{r/2} + 1)$ is a multiple of $N$. Unless one of the two factors is itself a multiple of $N$, each shares a nontrivial divisor with $N$, and the greatest common divisors give the factors. For $r = 4$, $7^2 = 49$. By Euclid's algorithm, $48 = 3\cdot 15 + 3$ and $15 = 5 \cdot 3$, so $\gcd(48, 15) = 3$; and $50 = 3\cdot 15 + 5$, $15 = 3\cdot 5$, so $\gcd(50, 15) = 5$. So $15 = 3 \times 5$.

A run fails if $r$ is odd, or if $a^{r/2} \equiv -1 \pmod N$, because then $a^{r/2}+1$ is a multiple of $N$ and the gcds are 1 and $N$. For $a = 14 \equiv -1 \pmod{15}$ the order is 2 and $14^1 \equiv -1$. If $\gcd(a, N) \neq 1$ you already have a factor. Choose $a$ at random and try again after a failure: for $N$ with at least two distinct odd prime factors, a random $a$ works with probability at least $1/2$.

## The quantum part

The map $U|y\rangle = |7y \bmod 15\rangle$ is unitary. Its eigenvalues are $e^{2\pi i\,s/r}$ for $s = 0, \dots, r-1$, and $|1\rangle$ is an equal superposition of the matching eigenvectors. Phase estimation (lesson 2.8) on $U$ with the work register in $|1\rangle$ therefore measures $s/r$ for a random $s$. With 4 counting qubits and $r = 4$, the possible outcomes are $m = 16s/4 = 0, 4, 8, 12$, each with probability $1/4$.

## From a measurement to $r$

The outcome $m$ is an estimate $m/16$ of $s/r$, and $r$ is the denominator of that fraction in lowest terms. For $m = 12$, $12/16 = 3/4$ and $r = 4$; for $m = 4$, $1/4$ gives 4 too. Two outcomes fail. For $m = 0$ the fraction is $0$ and gives $r = 1$. For $m = 8$ the fraction is $1/2$ and gives $r = 2$, but $7^2 \bmod 15 = 4 \neq 1$: here $s = 2$ shares a factor with $r$, and the denominator is $r/\gcd(s, r)$. So check that $a^r \equiv 1$ before using $r$, and combine several runs.

When $m/2^t$ is only an approximation of $s/r$, a continued fraction finds the fraction with a small denominator. Take $t = 8$ and $m = 191$: $191/256 = 0.746$ expands as $[0; 1, 2, 1, 15, 4]$, with convergents $0, 1, \tfrac23, \tfrac34, \tfrac{47}{63}, \dots$ The last with denominator at most 15 is $3/4$, so $r = 4$. In Python, `Fraction(191, 256).limit_denominator(15)` does this. It is guaranteed to work when $2^t \ge N^2$, which needs $t = 8$ for $N = 15$. With $t = 4$ it works here only because the estimates are exact.

```python
from fractions import Fraction
Fraction(12, 16).limit_denominator(15)   # 3/4, so r = 4
```

In the lab, `apply_controlled_mod_mult(qc, control, power)` multiplies the work register (qubits 4 to 7) by $7^{\text{power}} \bmod 15$ when qubit `control` is 1, and `inverse_qft(qc, qubits)` is the inverse QFT of 2.7.
