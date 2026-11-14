## The problem

Alice has a qubit in an unknown state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ and wants Bob, who is far away, to have that state. She cannot measure the qubit and send the result: a measurement yields one bit and destroys the superposition. She cannot copy it either, because the **no-cloning theorem** forbids copying an unknown quantum state.

## The resource: an entangled pair

Alice and Bob share a Bell pair created beforehand: qubit 1 is with Alice and qubit 2 with Bob. With this pair and two bits of classical communication, **quantum teleportation** transfers the state of qubit 0 to qubit 2.

## The protocol

1. Create a Bell pair on qubits 1 and 2: $H$ on qubit 1, then CNOT from 1 to 2.
2. Alice applies CNOT from qubit 0 to qubit 1, then $H$ on qubit 0.
3. Alice measures qubits 0 and 1 and sends the two bits to Bob.
4. Bob applies $X$ if the bit from qubit 1 is $1$, then $Z$ if the bit from qubit 0 is $1$.

After step 3, Bob's qubit is in one of four states, according to the measurement result. Each is $|\psi\rangle$ altered by a known Pauli operator, and step 4 undoes it. Labels are $|q_1 q_0\rangle$ of the measured bits:

| Measured bits (q1 q0) | Bob's state | Correction |
| :-- | :-- | :-- |
| 00 | $\alpha|0\rangle + \beta|1\rangle$ | none |
| 01 | $\alpha|0\rangle - \beta|1\rangle$ | $Z$ |
| 10 | $\beta|0\rangle + \alpha|1\rangle$ | $X$ |
| 11 | $-\beta|0\rangle + \alpha|1\rangle$ | $X$, then $Z$ |

## Conditional gates in Qiskit

A gate that depends on a measured bit is written as

```python
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
```

## No faster-than-light signaling

Before the two bits arrive, Bob's qubit is in each of the four states of the table with probability $1/4$. This mixture is the same for every $|\psi\rangle$ (it is the maximally mixed state), so Bob's measurements reveal nothing about $|\psi\rangle$. The transfer depends on the classical message, which cannot travel faster than light. Alice's original state is also gone: her measurement leaves qubits 0 and 1 in computational basis states, so no copy exists.

## Deferred measurement

If Alice and Bob are not separated, so that gates may act on qubits 0 and 2 together, the measurements and classically controlled gates can be replaced by controlled gates applied before any measurement: `qc.cx(1, 2)` instead of the $X$ conditioned on qubit 1, and `qc.cz(0, 2)` instead of the $Z$ conditioned on qubit 0. Bob's final state is the same. This is the **principle of deferred measurement**. In this lesson the separation is part of the protocol, so the corrections must use the classical bits.

## In the lab

The Alice × Bob tab compares Alice's original state with Bob's current state. Step through the circuit with the timeline, and use "Draw again" to sample other measurement outcomes. With the correct conditional gates, Bob's state equals Alice's original state for every outcome.
