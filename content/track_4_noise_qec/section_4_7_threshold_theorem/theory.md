## Feeding the code its own output

With physical error probability $p=0.01$ per qubit and a perfect correcting circuit, the three-qubit bit-flip code fails with probability

$$
f(p) = 3p^2(1-p) + p^3 = 3p^2 - 2p^3 ,
$$

so $f(0.01) = 2.98\times10^{-4}$. Now treat the encoded qubit as a new physical qubit with that error rate and encode three of them with the same code. The second level fails with probability $f(2.98\times10^{-4}) = 2.66\times10^{-7}$, the third with $2.1\times10^{-13}$, the fourth with $1.4\times10^{-25}$. This is **concatenation**: level $k$ uses $3^k$ physical qubits per logical qubit, and its error rate is the map applied to the level below, $p_k=f(p_{k-1})$ with $p_0=p$.

For small $p$ the map is about $3p^2$, so each level squares the error rate and multiplies by 3. If a code fails only when two errors hit one of $c$ possible pairs of locations, then $p_k \approx c\,p_{k-1}^2$, and solving this gives

$$
p^{(k)} \approx \frac{(c\,p)^{2^k}}{c} .
$$

For $c=3$ and $p=0.01$ it gives $2.7\times10^{-7}$ after two levels and $2.2\times10^{-13}$ after three, close to the exact values. The exponent $2^k$ is what matters: when $c\,p<1$ the error rate falls doubly exponentially in the number of levels, and when $c\,p>1$ the same formula grows.

## Two numbers that are not the threshold

The map $f$ has fixed points at $p=0$, $p=1/2$ and $p=1$. Below $1/2$ we have $f(p)<p$, above it $f(p)>p$. From $p=0.6$ the error rate climbs, $0.648$, $0.716$, $0.803$, toward 1, and from $p=0.4$ it falls, $0.352$, $0.284$, $0.197$. The point $p=1/2$ is therefore where encoding stops helping in this idealised model. It is the **pseudo-threshold** of the code, the same value as in lesson 4.2, and lesson 4.8 finds one for the Shor code.

The crude model gives another number, $1/c=1/3$, because $(cp)^2/c$ is only the leading term of $f$ and is inaccurate when $p$ is not small. Neither 1/2 nor 1/3 is the threshold that the next section is about.

## What fault tolerance adds

The calculation above assumed that the circuit that measures the syndrome and corrects is perfect. It is not: it is made of the same noisy gates. Worse, a single fault can do more damage than one error. A CNOT that copies a parity out of a data qubit can carry a fault from the ancilla back into several data qubits, and then one fault produces two errors in a block that the code can correct only one of. The extraction circuit also adds many new places where a fault can strike, so the number $c$ of pairs of locations that can fail together is much larger than 3.

**Fault-tolerant** design arranges every gate and every syndrome extraction so that one fault in a gate spreads to at most one error per block, which restores the quadratic suppression in the formula above, with a larger $c$. The **threshold theorem** (Nielsen & Chuang, p. 481) says that a computation of size $n$ can then be done with error at most $\epsilon$ using $O(\mathrm{poly}(\log(n/\epsilon))\,n)$ gates, as long as the error per physical operation is below a constant threshold $p_{\mathrm{th}}$. This $p_{\mathrm{th}}$ is roughly $1/c$ for the full fault-tolerant circuit, far below 1/2. The theorem needs the noise to be independent or only weakly and locally correlated, fresh ancilla qubits to extract the syndrome again and again, and operations on different qubits to run in parallel so that idle qubits do not wait and accumulate errors.

To reach a target error $\epsilon$ for $n$ operations one needs $p^{(k)}\le\epsilon/n$. Because $p^{(k)}$ falls doubly exponentially, $2^k$ grows only like $\log(n/\epsilon)$, so the qubit overhead $3^k$ grows as a power of $\log(n/\epsilon)$ and not as a power of $n$.

## Levels and qubits for a target

Starting from $p=0.01$, reaching $10^{-15}$ takes four levels, since $p_3=2.1\times10^{-13}$ is still above it and $p_4=1.4\times10^{-25}$ is far below. That is $3^4=81$ physical qubits per logical qubit. Starting above the pseudo-threshold no number of levels is enough.
