## Two qubits

Two qubits have four computational basis states, $|00\rangle$, $|01\rangle$, $|10\rangle$ and $|11\rangle$, and a general state is

$$
|\psi\rangle = a_{00}|00\rangle + a_{01}|01\rangle + a_{10}|10\rangle + a_{11}|11\rangle
$$

With $n$ qubits there are $2^n$ amplitudes. This growth is why simulating quantum computers on classical ones becomes hard.

## Qubit ordering

This platform follows Qiskit: qubit 0 is the rightmost label, so in $|q_1 q_0\rangle$ the state $|01\rangle$ has qubit 0 in $1$ and qubit 1 in $0$. This is the ordering of a binary number, with the least significant bit on the right.

Nielsen & Chuang, and many other texts, write qubit 0 on the left, so the same state is labeled $|10\rangle$ there. Check which convention a source uses before comparing labels.

## Product states and entangled states

When each qubit has its own state, the joint state is the **tensor product**:

$$
|q_1\rangle \otimes |q_0\rangle = |+\rangle \otimes |0\rangle = \frac{|00\rangle + |10\rangle}{\sqrt{2}}
$$

Here qubit 1 is in $|+\rangle$ and qubit 0 is in $|0\rangle$. The left factor is the qubit with the higher index.

Some states cannot be written as a product. An example is the Bell state

$$
|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

No pair of single-qubit states has $|\Phi^+\rangle$ as its tensor product. The qubits are **entangled**: only the pair has a definite state. The four Bell states, $|\Phi^\pm\rangle$ and $|\Psi^\pm\rangle$, are maximally entangled and form a basis of the two-qubit state space.

## The CNOT gate

The controlled-NOT (CNOT) gate acts on a **control** qubit and a **target** qubit. It flips the target if the control is $1$ and does nothing otherwise. With the control in superposition it creates entanglement:

$$
\text{CNOT}\,\frac{|00\rangle + |01\rangle}{\sqrt{2}} = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

Here qubit 0 is the control, and it is in $|+\rangle$ while qubit 1 is in $|0\rangle$.

## A test for product states

A pure two-qubit state is a product state if and only if

$$
a_{00}\,a_{11} = a_{01}\,a_{10}
$$

For $|\psi\rangle = (\alpha_1|0\rangle + \beta_1|1\rangle)\otimes(\alpha_0|0\rangle + \beta_0|1\rangle)$ we have $a_{00}a_{11} = \alpha_1\alpha_0\beta_1\beta_0 = a_{01}a_{10}$. For $|\Phi^+\rangle$, $a_{00}a_{11} = \tfrac{1}{2}$ and $a_{01}a_{10} = 0$, so it is entangled.

Counting nonzero amplitudes is not enough. The state $(|00\rangle + |01\rangle - |10\rangle - |11\rangle)/2$ has four nonzero amplitudes but passes the test: it equals $|-\rangle\otimes|+\rangle$.

## In the lab

- Q-Sphere: each point is a basis state. The more $1$s in the label, the further south the point. Size shows probability and color shows phase.
- Bloch spheres: a qubit that is entangled with another has no pure state of its own, and its vector shrinks toward the center ($|r| < 1$). For $|\Phi^+\rangle$, $|r| = 0$.
- Entanglement: the concurrence is $0$ for a product state and $1$ for a maximally entangled state.
