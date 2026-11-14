## One level

The three-qubit bit-flip code fails when two or three of its qubits flip. If each qubit flips independently with probability $p$ and the correction is perfect, the encoded qubit is wrong with probability

$$
f(p) = 3p^2(1-p) + p^3 = 3p^2 - 2p^3 .
$$

For small $p$ this is about $3p^2$, much smaller than $p$. For example, $f(0.01) = 2.98\times10^{-4}$. The map $f$ has fixed points at $p=0$, $p=1/2$ and $p=1$. Between $0$ and $1/2$ we have $f(p)<p$, and above $1/2$ we have $f(p)>p$, so $p = 1/2$ is the **threshold** of this idealised code: below it, encoding helps, above it, encoding hurts.

## Concatenation

**Concatenation** encodes each of the three qubits of the code again with the same code, and repeats this $k$ times. Level $k$ uses $3^k$ physical qubits per logical qubit, and the error rate at each level is the map applied to the level below:

$$
p_k = f(p_{k-1}), \qquad p_0 = p .
$$

Near the origin, $f(p) \approx 3p^2$, so each level squares the error rate and multiplies by 3. Generally, if a code fails only when two errors happen at some pair out of $c$ possible pairs of locations, $p_{k} \lesssim c\,p_{k-1}^2$. Solving this recursion gives

$$
p_L^{(k)} \approx \frac{(c\,p)^{2^k}}{c} .
$$

For $c\,p < 1$ the exponent $2^k$ makes this fall doubly exponentially in $k$. The condition $c\,p<1$ defines the threshold $p_{\mathrm{th}} = 1/c$. For the three-qubit code $c = 3$, so the model gives $1/3$. The exact map has the fixed point $1/2$ instead, because $(cp)^{2}/c$ is only the leading term of $f$ and is inaccurate when $p$ is not small. Real thresholds are lower than both numbers because the gates that measure the syndrome also fail, which increases $c$.

## The theorem

The **threshold theorem** (Nielsen & Chuang, p. 481): a quantum computation of size $n$ can be done with error at most $\epsilon$ using $O\big(\mathrm{poly}(\log(n/\epsilon))\,n\big)$ gates, provided the error per physical operation is below a constant threshold $p_{\mathrm{th}}$ and the noise satisfies these assumptions:

- errors act independently on different qubits, or are correlated only weakly and locally;
- fresh ancilla qubits in a known state are available, so the syndrome can be extracted again and again;
- gates can act on disjoint qubits in parallel, so errors do not accumulate while one part of the computer waits for another;
- the operations needed for the algorithm and for the correction can be done fault-tolerantly, so that one fault in a gate spreads to at most one error per block.

To reach a target error $\epsilon$ for a computation with $n$ operations, one needs $p_L^{(k)} \le \epsilon/n$. Because $p_L^{(k)}$ falls doubly exponentially, $2^k$ grows only like $\log(n/\epsilon)$, and the overhead $3^k$ in qubits grows as a power of $\log(n/\epsilon)$, not as a power of $n$. This is why the overhead is polylogarithmic.

## Numbers

From $p = 0.01$ with the exact map: $p_1 = 2.98\times10^{-4}$, $p_2 = 2.65\times10^{-7}$, $p_3 = 2.1\times10^{-13}$, $p_4 = 1.4\times10^{-25}$. Reaching $10^{-15}$ takes four levels and $3^4 = 81$ physical qubits per logical qubit. From $p=0.6$, each level makes the error rate larger.
