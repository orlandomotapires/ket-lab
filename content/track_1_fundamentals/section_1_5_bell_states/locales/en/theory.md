## Two qubits

With two qubits there are four basis states: $|00\rangle$, $|01\rangle$, $|10\rangle$ and $|11\rangle$. A general state is a combination of the four:

$$
|\psi\rangle = a_{00}|00\rangle + a_{01}|01\rangle + a_{10}|10\rangle + a_{11}|11\rangle
$$

With $n$ qubits there are $2^n$ amplitudes. This growth is what makes it hard for classical computers to simulate quantum computers.

## Qubit ordering

On this platform, as in Qiskit, **qubit 0 is on the right** in the label: in $|q_1 q_0\rangle$, the state $|01\rangle$ means qubit 0 in $1$ and qubit 1 in $0$. The convention looks reversed at first, but it is the same as a binary number: the least significant bit is on the right.

> **Note:** many textbooks and courses write qubit 0 on the **left**. When you compare with another source, the labels appear reversed: what is $|01\rangle$ here is $|10\rangle$ there. When reading a result, always check which convention is in use.

## States that separate and states that do not

If each qubit has its own state, the joint state is the **tensor product** of the two:

$$
|q_1\rangle \otimes |q_0\rangle = |+\rangle \otimes |0\rangle = \frac{|00\rangle + |10\rangle}{\sqrt{2}}
$$

Here qubit 1 is in $|+\rangle$ and qubit 0 is in $|0\rangle$. The left factor is always the one with the higher index, following the convention above.

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

## A test for products

For a pure state of two qubits there is a simple test. It is separable (a product) if and only if

$$
a_{00}\,a_{11} = a_{01}\,a_{10}
$$

If $|\psi\rangle = (\alpha_1|0\rangle + \beta_1|1\rangle)\otimes(\alpha_0|0\rangle + \beta_0|1\rangle)$, then $a_{00}a_{11} = \alpha_1\alpha_0\beta_1\beta_0 = a_{01}a_{10}$. For $|\Phi^+\rangle$, $a_{00}a_{11} = \tfrac{1}{2}$ but $a_{01}a_{10} = 0$: it is not a product, so it is entangled. On the other hand, $(|00\rangle + |01\rangle - |10\rangle - |11\rangle)/2$ has all four amplitudes nonzero and passes the test, because it is $|-\rangle\otimes|+\rangle$. Counting nonzero amplitudes is not enough.

## What to watch in the lab

- **Q-Sphere**: each point is a basis state. Points sit further south the more $1$s the label has; the size indicates the probability and the color, the phase.
- **Bloch spheres**: an entangled qubit has no state of its own. Its vector shrinks to the center of the sphere ($|r| = 0$).
- **Entanglement**: the concurrence ranges from $0$ (separable state) to $1$ (maximal entanglement).
