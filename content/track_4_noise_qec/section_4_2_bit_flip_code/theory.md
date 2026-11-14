## Redundancy without copying

Real gates and qubits are noisy, and long computations need errors to be detected and removed along the way. Three obstacles seem to forbid this: an unknown state cannot be copied (no-cloning theorem), measuring a qubit destroys its superposition, and errors take a continuum of values. Quantum error correction avoids the first two by entangling instead of copying, and the third by measuring discrete syndromes.

Classically one repeats a bit, $0\to000$, and takes the majority. For a qubit, the state is spread over three qubits with two CNOT gates:

$$
\alpha|0\rangle + \beta|1\rangle \;\longrightarrow\; \alpha|000\rangle + \beta|111\rangle
$$

This is the **three-qubit bit-flip code**. The result is one logical qubit, not three copies of $|\psi\rangle$.

## Syndrome measurement

A bit flip on qubit 1 gives $\alpha|010\rangle + \beta|101\rangle$. Measuring the qubits would reveal $\alpha$ and $\beta$ only statistically and collapse the state. The parities of pairs of qubits, however, are the same for both terms, so they carry no information about $\alpha$ and $\beta$. Two ancillas store the parity of qubits 0 and 1 and of qubits 1 and 2. This pair of bits is the **syndrome**:

| Syndrome (a₃ a₄) | Error | Correction |
| :-- | :-- | :-- |
| 00 | none | none |
| 10 | X on qubit 0 | X on qubit 0 |
| 11 | X on qubit 1 | X on qubit 1 |
| 01 | X on qubit 2 | X on qubit 2 |

The correction can be applied without measuring, with Toffoli gates controlled by the ancillas (deferred measurement principle). Here the ancillas are ordered as in the table, with a₃ on qubit 3 and a₄ on qubit 4.

## What the code does not correct

- Two bit flips produce the syndrome of a single flip on the third qubit. The "correction" then flips all three qubits, which is a logical $X$.
- A phase flip $Z$ on any qubit changes no parity, so the syndrome is 00. It acts on the code as a logical $Z$ and is not detected. The same construction in the Hadamard basis corrects phase flips instead, and Shor's nine-qubit code combines both and corrects an arbitrary error on one qubit.

## The threshold

Suppose each of the three qubits suffers a bit flip independently with probability $p$, and the encoding, syndrome measurement and correction are perfect. The code fails when two or three qubits flip, with probability $3p^2(1-p)+p^3 = 3p^2-2p^3$. The logical error probability is

$$
p_L = 3p^2 - 2p^3
$$

and the success probability is $1 - 3p^2 + 2p^3$. The code helps when $p_L < p$, that is, $(1-p)(1-2p) > 0$, so for $p < \tfrac12$. This value is the **threshold** of this code. For small $p$ the logical error is quadratic in $p$. Fault-tolerant quantum computing relies on the same idea: below a threshold error rate, encoding reduces the error.

## In the lab

- The buttons choose the injected error. Try the ones the code does not correct.
- Register: with the cursor after the syndrome, the ancilla bits appear.
- Bloch spheres: the state of each data qubit.
- Threshold: the protected qubit compared with an unprotected one.
