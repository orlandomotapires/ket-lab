## The problem

Alice has a qubit in a state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ that she **does not know**, and she wants to deliver it to Bob, who is far away. She cannot measure the qubit and send the numbers: a measurement gives only one bit and destroys the superposition. She also cannot copy it: the **no-cloning theorem** forbids copying an unknown quantum state.

## The resource: an entangled pair

Before separating, Alice and Bob created a Bell pair: qubit 1 stayed with Alice and qubit 2 with Bob. With this pair and **two bits of classical communication**, the state can be transferred.

## The protocol

1. **Bell pair** between qubits 1 and 2: $H$ on qubit 1 and CNOT from 1 to 2.
2. **Alice entangles** her state with her half of the pair: CNOT from 0 to 1, then $H$ on qubit 0.
3. **Alice measures** qubits 0 and 1 and sends the two bits to Bob.
4. **Bob corrects**: he applies $X$ if the bit from qubit 1 is $1$ and then $Z$ if the bit from qubit 0 is $1$.

After step 3, Bob's qubit is in one of four states, depending on the measurement result. Each one is $|\psi\rangle$ with a known "defect", and the correction in step 4 undoes exactly that defect:

| Measured bits (q1 q0) | Bob's state | Correction |
| :-- | :-- | :-- |
| 00 | $\alpha|0\rangle + \beta|1\rangle$ | none |
| 01 | $\alpha|0\rangle - \beta|1\rangle$ | $Z$ |
| 10 | $\beta|0\rangle + \alpha|1\rangle$ | $X$ |
| 11 | $\beta|0\rangle - \alpha|1\rangle$ | $X$, then $Z$ |

## Conditional corrections in Qiskit

A gate that depends on a measured bit is written like this:

```python
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
```

## Nothing travels faster than light

Without the two bits, Bob has a 25% chance of each of the four states, and this mixture carries no information about $|\psi\rangle$. Teleportation depends on the classical message, which travels at most at the speed of light.

## In the lab

The **Alice × Bob** tab compares Alice's original state with Bob's current state. Use the timeline to follow the protocol step by step and "Draw again" to see other measurement outcomes: with the right corrections, Bob ends up equal to Alice in all of them.
