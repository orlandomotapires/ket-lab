## Two bits in one qubit

Without any prior arrangement, one qubit carries at most one classical bit to the receiver (Holevo's theorem). Suppose now that Alice and Bob met earlier and each took one qubit of a Bell pair. Alice can then send two bits by acting on her half and shipping that single qubit to Bob. This is **superdense coding**, and the qubit that travels is the only quantum communication in the protocol.

Here Alice holds qubit 1 and Bob holds qubit 0, so a two-qubit label $|q_1q_0\rangle$ lists Alice's qubit first. The pair is $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$.

## Encoding

A Pauli gate on one qubit of $|\Phi^+\rangle$ turns it into another Bell state, and the four Bell states are orthogonal. Applying $Z$ to qubit 1 gives $(|00\rangle - |11\rangle)/\sqrt{2}$; applying $X$ gives $(|01\rangle + |10\rangle)/\sqrt{2}$; applying both gives $(|01\rangle - |10\rangle)/\sqrt{2}$ up to a global sign. Alice assigns the four messages $b_1b_0$ in the order $00 \to I$, $01 \to X$, $10 \to Z$, $11 \to ZX$. The first bit selects whether $Z$ is applied and the second whether $X$ is, with $X$ acting first.

## Decoding

Bob now has both qubits and must tell four orthogonal states apart. He measures in the Bell basis, which in lesson 1.6 meant running the pair-creation circuit backwards. Take the message $10$, so the state is $|\Phi^-\rangle = (|00\rangle - |11\rangle)/\sqrt{2}$. A CNOT with qubit 1 as control and qubit 0 as target turns $|11\rangle$ into $|10\rangle$, leaving

$$
\frac{|00\rangle - |10\rangle}{\sqrt{2}} = \frac{|0\rangle - |1\rangle}{\sqrt{2}}\otimes|0\rangle = |-\rangle|0\rangle .
$$

Then $H$ on qubit 1 takes $|-\rangle$ to $|1\rangle$, so the state is $|10\rangle$ and measuring returns the message $10$. The other three cases end in $|00\rangle$, $|01\rangle$ and $|11\rangle$ for $|\Phi^+\rangle$, $|\Psi^+\rangle$ and $|\Psi^-\rangle$. It is easy to read the two bits in the wrong order here: qubit 1 holds the first bit of the message, and it is the left one in the label.

## What Bob has before the qubit arrives

Each qubit of a Bell pair, taken alone, is in the maximally mixed state $I/2$ (the reduced state of lesson 1.6). Alice's gate on qubit 1 does not change what Bob's qubit looks like, so nothing about the message can be read from it. The message is in the correlations between the two qubits, which Bob can use only once he holds both. The same argument shows that someone who intercepts the traveling qubit alone also learns nothing.

Teleportation (lesson 1.6) uses the same resource in the opposite direction: a Bell pair and two classical bits move one qubit, while here a Bell pair and one qubit move two classical bits.

## Check it

The validator runs your code for all four messages. Before you do, predict the amplitude table after Alice's gates for the message $01$, then compare. The creation of the pair and Bob's decoding must be the same for every message, and between the two CNOT gates only qubit 1 may be touched.
