## A state Alice cannot send

Alice holds a qubit in an unknown state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ and Bob, far away, needs it. Measuring the qubit gives one bit and destroys the superposition, so she cannot just read $\alpha$ and $\beta$ and send them. Copying is out too, by the no-cloning theorem of lesson 1.8. What she and Bob can have is a Bell pair made beforehand, with one qubit each, plus an ordinary channel for two classical bits.

The Bell pair of lesson 1.5 is half of what is needed. The other half is a way to measure Alice's two qubits, 0 and 1, so that the result says how they are related instead of what each one holds. That is a measurement in the Bell basis. Lesson 1.5 built $|\Phi^+\rangle$ with $H$ and then CNOT; run backwards, CNOT and then $H$ turn the four Bell states into the four basis states $|00\rangle$ to $|11\rangle$, and an ordinary measurement reads out which one it was.

## Following the amplitudes

The pair sits on qubits 1 and 2, and Alice applies CNOT from 0 to 1 and then $H$ on qubit 0. For this derivation I write the qubits in the order 0, 1, 2 from left to right, the opposite of Qiskit's labels, so that Alice's two qubits come first. The initial state is

$$
\frac{1}{\sqrt{2}}\bigl(\alpha|0\rangle + \beta|1\rangle\bigr)\bigl(|00\rangle + |11\rangle\bigr)
= \frac{1}{\sqrt{2}}\bigl(\alpha|000\rangle + \alpha|011\rangle + \beta|100\rangle + \beta|111\rangle\bigr).
$$

The CNOT flips qubit 1 when qubit 0 is 1, so the four terms become $\alpha|000\rangle + \alpha|011\rangle + \beta|110\rangle + \beta|101\rangle$ (divided by $\sqrt{2}$). Then $H$ sends $|0\rangle$ on qubit 0 to $(|0\rangle + |1\rangle)/\sqrt{2}$ and $|1\rangle$ to $(|0\rangle - |1\rangle)/\sqrt{2}$, and we collect the terms by what Alice's qubits show. Take the outcome in which both read 1. Two terms have qubit 1 equal to 1, namely $\alpha|011\rangle$ and $\beta|110\rangle$. After $H$, the first gives $|1\rangle$ on qubit 0 with a plus sign and leaves $\alpha|1\rangle$ on Bob's qubit. The second gives $|1\rangle$ on qubit 0 with a minus sign, from the minus in $H|1\rangle$, and leaves $-\beta|0\rangle$ on Bob's qubit. Bob's qubit is then $-\beta|0\rangle + \alpha|1\rangle$.

This is the outcome people tend to get wrong, because two things have happened to $|\psi\rangle$: its amplitudes are swapped and one sign is flipped. Bob applies $X$ to fix the swap, which gives $\alpha|0\rangle - \beta|1\rangle$, and then $Z$ to fix the sign, which gives $\alpha|0\rangle + \beta|1\rangle$. The same bookkeeping for the other three outcomes gives the table, with the measured bits listed as $q_1q_0$:

| Bits $q_1 q_0$ | Bob's qubit | Correction |
| :-- | :-- | :-- |
| 00 | $\alpha|0\rangle + \beta|1\rangle$ | none |
| 01 | $\alpha|0\rangle - \beta|1\rangle$ | $Z$ |
| 10 | $\beta|0\rangle + \alpha|1\rangle$ | $X$ |
| 11 | $-\beta|0\rangle + \alpha|1\rangle$ | $X$, then $Z$ |

Each outcome has probability $1/4$ whatever $\alpha$ and $\beta$ are. The bit from qubit 1 selects $X$ and the bit from qubit 0 selects $Z$. In Qiskit a gate that depends on a measured bit reads

```python
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
```

## Why this is not faster than light, and not a copy

Before Bob receives the two bits, his qubit is one of the four states of the table, each with probability $1/4$. Averaged over them it is the **maximally mixed state**, which gives 0 and 1 with probability $1/2$ in every basis and sits at the center of the Bloch sphere, like either qubit of a Bell pair alone. Such a description is a **reduced state**: it is what remains for one part of a system when you ignore the rest. It is the same for every $|\psi\rangle$, so no measurement of Bob's tells him anything before the message arrives. Alice's measurement leaves her qubits in basis states that carry no information about $|\psi\rangle$, so after the protocol exactly one copy of the state exists.

## When the parties are not apart

If gates may act on qubits 0 and 2 together, measuring and then correcting can be replaced by controlled gates applied first: `qc.cx(1, 2)` for the $X$ and `qc.cz(0, 2)` for the $Z$, with the measurements dropped. Bob's final state is the same. This is the principle of deferred measurement, and the challenge asks for that version. In the mission the separation is part of the problem, so the corrections have to use the classical bits.
