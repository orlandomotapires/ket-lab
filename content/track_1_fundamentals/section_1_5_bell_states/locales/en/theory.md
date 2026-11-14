## Two qubits

With two qubits there are four basis states: $|00\rangle$, $|01\rangle$, $|10\rangle$ and $|11\rangle$. A general state is a combination of the four:

$$
|\psi\rangle = a_{00}|00\rangle + a_{01}|01\rangle + a_{10}|10\rangle + a_{11}|11\rangle
$$

With $n$ qubits there are $2^n$ amplitudes. This growth is what makes it hard for classical computers to simulate quantum computers.

## Qubit ordering

On this platform, as in Qiskit, **qubit 0 is on the right** in the label: in $|q_1 q_0\rangle$, the state $|01\rangle$ means qubit 0 in $1$ and qubit 1 in $0$. The convention looks reversed at first, but it is the same as a binary number: the least significant bit is on the right.

## States that separate and states that do not

If each qubit has its own state, the joint state is the **tensor product** of the two:

$$
|+\rangle \otimes |0\rangle = \frac{|00\rangle + |10\rangle}{\sqrt{2}}
$$

Some two-qubit states **cannot** be written this way. The most famous is the Bell state

$$
|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

There is no state of qubit 0 and state of qubit 1 whose product gives $|\Phi^+\rangle$. The two qubits are **entangled**: the state exists only for the pair.

## The CNOT gate

The CNOT (*controlled NOT*) acts on two qubits: it flips the **target** when the **control** is $1$ and does nothing when it is $0$. Applied to a superposition on the control, it creates entanglement:

$$
\text{CNOT}\,\frac{|00\rangle + |01\rangle}{\sqrt{2}} = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

## What to watch in the lab

- **Q-Sphere**: each point is a basis state. Points sit further south the more $1$s the label has; the size indicates the probability and the color, the phase.
- **Bloch spheres**: an entangled qubit has no state of its own. Its vector shrinks to the center of the sphere ($|r| = 0$).
- **Entanglement**: the concurrence ranges from $0$ (separable state) to $1$ (maximal entanglement).
