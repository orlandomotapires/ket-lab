## Does nine beat one?

The Shor code of lesson 4.4 corrects any error on one qubit, but it uses nine qubits, and every one of them can fail. So below which physical error rate does the encoded qubit really do better than a bare one? This project answers that exactly, by counting.

Between encoding and decoding the noise is a Pauli pattern, one letter $I$, $X$, $Y$ or $Z$ per qubit. Majority-vote decoding turns every pattern into a Pauli on the logical qubit, possibly $I$, and a Pauli error is all there is to track (Nielsen & Chuang §10.3.1). Under the depolarizing channel (§8.3.4) each qubit gets $I$ with probability $1-p$ and $X$, $Y$, $Z$ with probability $p/3$ each, so a pattern with $w$ errors has probability $(p/3)^w(1-p)^{9-w}$. The logical failure probability is the sum of this over the patterns whose logical Pauli is not $I$. A bare qubit fails with probability $p$, and the **pseudo-threshold** $p^*$ is the smallest $p>0$ where the two are equal: below it the code helps, above it the nine qubits add more errors than they remove.

## A count you can do by hand

Every single error is corrected, so the smallest failing patterns have two errors. There are $\binom{9}{2}=36$ pairs of qubits and 9 pairs of letters for each, so 324 two-error patterns. Which fail?

Two qubits in the same block with $X$ or $Y$ on each: the inner vote sees two bit flips and flips the third qubit as well, leaving $X\otimes X\otimes X$ on the block, which is a logical $Z$. There are 9 pairs of qubits in the same block and $2\times2$ letters, so 36 patterns. Two qubits in different blocks, each with $Y$ or $Z$: each block carries an odd number of phase flips, the leaders vote wrongly and a logical $X$ remains. There are 27 pairs in different blocks and $2\times2$ letters, so 108 patterns. Everything else is corrected, for a total of $36+108=144$ failing patterns out of 324.

Each failing pattern has probability about $(p/3)^2$, so for small $p$

$$
p_L \approx 144\,\frac{p^2}{9} = 16\,p^2 .
$$

At $p=0.01$ this is $1.6\times10^{-3}$ (the exact sum is $1.54\times10^{-3}$), already six times smaller than the bare 0.01. At $p=0.1$ the approximation is no longer valid: the exact value, 0.112, is already above the bare qubit.

## From patterns to an exact sum

Enumerating all $4^9=262144$ patterns is possible, but the structure allows something faster. Reduce each block to two bits: whether its inner vote fails (at least two of its three qubits carry $X$ or $Y$) and whether it carries an odd number of $Y$ or $Z$. A failed vote leaves $X$ on the leader, which is a logical $Z$ when it happens in an odd number of blocks. An odd phase flip in at least two blocks beats the vote on the leaders and leaves a logical $X$. Both together make $Y$. Enumerating the $4^3=64$ patterns of one block, then combining three blocks, gives the same number as the full enumeration.

In `error[q]` the entry $q$ is the Pauli on qubit $q$, so the first list entry is the leader of the first block.

## Where the crossover is

Setting $p_L(p)=p$ and solving numerically gives $p^*\approx0.085$. At $p=0.05$ the exact $p_L$ is 0.033, below the bare 0.05, and at $p=0.1$ it is 0.112, above 0.1. The value is not comparable with the 1/2 of lesson 4.7: that one counted only bit flips on three qubits, and this one counts all three Paulis on nine. In both cases the crossover says where encoding stops paying off for a code whose correcting circuit is perfect, which a real device cannot offer.
