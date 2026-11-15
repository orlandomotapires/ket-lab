## What to build

This project reuses the Shor code of lesson 4.4 and asks a quantitative question: below which physical error rate does encoding help? Four parts, checked independently.

1. **Decoder.** The circuit must correct X, Y and Z on any one of the nine qubits.
2. **Error pattern to logical Pauli.** Between encoding and decoding, the noise is a Pauli pattern, one letter I, X, Y or Z per qubit. Majority-vote decoding turns every pattern into a Pauli on the logical qubit (possibly I), and a Pauli error is all that has to be tracked (Nielsen & Chuang §10.3.1).
3. **Logical failure probability.** Under the depolarizing channel (Nielsen & Chuang §8.3.4) each qubit gets I with probability $1-p$ and X, Y, Z with probability $p/3$ each. The logical failure probability is
$$p_L(p)=\sum_{\text{patterns with logical Pauli}\neq I}\ \prod_{q}\Pr(e_q).$$
A bare qubit fails with probability $p$.
4. **Crossover.** The pseudo-threshold $p^*$ is the smallest $p>0$ with $p_L(p)=p$. Below it the code helps; above it the nine qubits add more errors than they remove.

## Counting

The nine qubits form three blocks. Within a block, the vote fails when at least two qubits carry X or Y, which leaves an X on the block leader; across the leaders this is a logical Z when it happens in an odd number of blocks. An odd number of Y or Z in a block is a Z on its leader, and when this happens in at least two blocks the leaders vote wrongly and a logical X remains. Enumerating $4^3=64$ patterns per block, and then three blocks, is exact and fast. Enumerating all $4^9=262144$ patterns gives the same number.

Qubit ordering: in this project `error[q]` is the Pauli on qubit q, with qubit 0 the first list entry and the block leader of the first block.

## Rubric

| Criterion | What is checked |
|---|---|
| 1 | qubit 0 recovered after X, Y, Z on each of the nine qubits, for several inputs |
| 2 | logical_pauli agrees with the decoder on many error patterns |
| 3 | logical_failure(p) within $10^{-6}$ of the exact value at five values of p |
| 4 | logical_failure(p) < bare_failure(p) for small p |
| 5 | p_star within 0.003 of the crossover |
