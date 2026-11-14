## The task

Alice wants to send Bob two classical bits $b_1 b_0$. Sending one qubit cannot carry more than one classical bit by itself, a bound given by Holevo's theorem. If Alice and Bob already share a Bell pair, one qubit sent from Alice to Bob is enough for two bits. The protocol is **superdense coding**.

## The shared pair

Before the protocol, a source prepares

$$|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

and gives one qubit to each party. In this lesson Alice holds qubit 1 and Bob holds qubit 0.

## Encoding

Alice applies a Pauli operator to her qubit, chosen by the message. The four results are the four Bell states, which are orthogonal:

| Message $b_1 b_0$ | Alice applies | Joint state |
| :-- | :-- | :-- |
| 00 | $I$ | $\dfrac{\lvert 00\rangle + \lvert 11\rangle}{\sqrt{2}}$ |
| 01 | $X$ | $\dfrac{\lvert 01\rangle + \lvert 10\rangle}{\sqrt{2}}$ |
| 10 | $Z$ | $\dfrac{\lvert 00\rangle - \lvert 11\rangle}{\sqrt{2}}$ |
| 11 | $ZX$ | $\dfrac{\lvert 01\rangle - \lvert 10\rangle}{\sqrt{2}}$ |

The first bit selects $Z$ and the second selects $X$, so the gate is $Z^{b_1}X^{b_0}$ applied to Alice's qubit, with $X$ acting first.

Alice then sends qubit 1 to Bob. This is the only qubit that travels.

## Decoding

Bob holds both qubits. Four orthogonal states can be told apart with certainty by a measurement in the Bell basis. Bob implements it by changing from the Bell basis to the computational basis: a CNOT with qubit 1 as control and qubit 0 as target, then $H$ on qubit 1. For $|\Phi^-\rangle$ the CNOT gives $(|0\rangle - |1\rangle)|0\rangle/\sqrt{2}$ in the order $q_1, q_0$, and $H$ turns the first factor into $|1\rangle$. The four cases are

$$|\Phi^+\rangle \to |00\rangle, \quad |\Psi^+\rangle \to |01\rangle, \quad |\Phi^-\rangle \to |10\rangle, \quad |\Psi^-\rangle \to |11\rangle ,$$

where each ket is $|q_1 q_0\rangle$. Measuring in the computational basis then returns the message with probability 1.

## What the receiver sees alone

Each Bell state has the reduced state $I/2$ on each qubit. Alice's operation on qubit 1 leaves Bob's reduced state unchanged, so Bob learns nothing about the message from his own qubit before the transfer. The information is in the joint state, and Bob has it only when both qubits are in his hands. This is consistent with the no-signaling principle: Alice cannot send information by acting on her half of the pair alone.

## Counting resources

The protocol uses one shared Bell pair and one transmitted qubit for two classical bits. Quantum teleportation (lesson 1.6) uses the same resource the other way: one Bell pair and two classical bits move one qubit.

## In the lab

The qubit labels follow Qiskit: $|q_1 q_0\rangle$ has qubit 0 on the right, so the message $b_1 b_0$ reads as the final label. Nielsen & Chuang put qubit 0 on the left, which swaps the roles of the two qubits in their equations.

The validator runs your code with each of the four messages. Between the two CNOT gates only qubit 1 may be touched, and the pair creation and the decoding must be identical for every message.
