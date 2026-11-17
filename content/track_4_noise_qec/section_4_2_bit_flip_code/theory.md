## Finding the flipped qubit without looking at it

Lesson 4.1 ended with a qubit that an $X$ error hits with probability $p$, say $p=0.1$. Nothing in that lesson lets you undo it, because you do not know the state, and you cannot find out without measuring, which destroys the superposition. Cloning is no way out either: the no-cloning theorem forbids copying an unknown state.

The classical remedy is to repeat the bit, $0\to000$, and take a majority vote. Quantum error correction keeps the idea but entangles instead of copying. Two CNOT gates from qubit 0 spread the state over three qubits:

$$
\alpha|0\rangle + \beta|1\rangle \;\longrightarrow\; \alpha|000\rangle + \beta|111\rangle .
$$

This is the **three-qubit bit-flip code**: one **logical qubit** stored in three physical qubits. It is not three copies of $|\psi\rangle$, and each qubit alone carries no trace of $\alpha$ and $\beta$.

## Parities reveal the error, not the state

Flip qubit 1. The state becomes $\alpha|010\rangle + \beta|101\rangle$. Measuring the qubits would give a random bit string and collapse the superposition. Compare instead qubit 0 with qubit 1: they differ in both terms. Compare qubit 1 with qubit 2: they differ in both terms. Because both terms of the state agree on every parity, asking for the parities teaches nothing about $\alpha$ and $\beta$, and still tells you where the flip happened.

Two ancilla qubits record the two parities, the first for qubits 0 and 1 and the second for qubits 1 and 2. The pair of bits $a_3a_4$ is the **syndrome**. Syndrome 00 means no error. 10 means qubit 0 flipped, since only the first parity changed. 11 points to qubit 1, which takes part in both parities, and 01 to qubit 2. The register view uses Qiskit ordering, so it prints the ancillas as $a_4a_3$, the reverse of the order written here.

The correction needs no measurement. A Toffoli gate controlled by both ancillas applies $X$ to a data qubit exactly when the syndrome points at it (the deferred measurement principle: a gate controlled by a measurement outcome can be replaced by a gate controlled by the qubit that would have been measured). For a pattern with a 0 in it, an $X$ on that ancilla before and after the Toffoli turns the 0 into the 1 that the gate expects.

## Two flips, or the wrong kind of flip

Flip qubits 0 and 1 together. The parities are 0 for qubits 0 and 1 and 1 for qubits 1 and 2, which is the syndrome of a single flip on qubit 2. The recovery flips qubit 2 as well, and all three qubits end up flipped: $\alpha|111\rangle+\beta|000\rangle$. That is a logical $X$, an error the code can no longer see.

A phase flip $Z$ on any qubit changes no parity, so the syndrome is 00 and nothing happens. On the code it acts as a logical $Z$, silently. The next lesson uses the same construction in the Hadamard basis to catch phase flips instead.

## How much the code helps

Let every qubit flip independently with probability $p$, with perfect encoding, syndrome and correction. The code fails when two or three qubits flip. At $p=0.1$ that is $3\times0.1^2\times0.9 = 0.027$ for exactly two, plus $0.1^3=0.001$ for all three, 0.028 in total, against 0.1 for one unprotected qubit. In general

$$
p_L = 3p^2(1-p) + p^3 = 3p^2 - 2p^3 .
$$

The code helps when $p_L<p$, which is $(1-p)(1-2p)>0$, so for $p<\tfrac12$. Call $p=1/2$ the **pseudo-threshold** of this idealised code. It is where encoding stops paying off in this model, and it is not the threshold of fault-tolerant computation, which also has to count errors made by the correcting circuit itself; lesson 4.7 draws that line. For small $p$ the logical error is quadratic: halving $p$ divides $p_L$ by about four.

## In the lab

Choose an error with the buttons and predict the outcome before you read the Bloch spheres: one flip, two flips, and a $Z$. Then run the three cases and check whether your prediction of the logical state held.
