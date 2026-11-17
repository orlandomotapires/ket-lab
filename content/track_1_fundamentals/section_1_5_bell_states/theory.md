## Two bits that are random and always equal

Apply $H$ to one qubit, then a CNOT from it to a second qubit, and measure both. Each qubit alone gives 0 or 1 with probability $1/2$, yet the two bits always agree. A pair of independent coins cannot do that, and no choice of one-qubit states for the two qubits can either. The state is **entangled**, and this lesson shows how to build it and how to recognize it.

## Two-qubit states and their labels

Two qubits have four basis states, $|00\rangle$, $|01\rangle$, $|10\rangle$ and $|11\rangle$, and a general state is $a_{00}|00\rangle + a_{01}|01\rangle + a_{10}|10\rangle + a_{11}|11\rangle$. With $n$ qubits there are $2^n$ amplitudes, which is why classical simulation of quantum circuits gets expensive so quickly.

The labels follow Qiskit: in $|q_1q_0\rangle$ qubit 0 is the rightmost, as in a binary number, so $|01\rangle$ means qubit 0 is 1. Nielsen & Chuang write qubit 0 on the left, and the same state is $|10\rangle$ there. Whenever you compare with a book, check which side it counts from.

If each qubit has its own state, the joint state is their **tensor product**. With qubit 1 in $|+\rangle$ and qubit 0 in $|0\rangle$,

$$
|+\rangle \otimes |0\rangle = \frac{|00\rangle + |10\rangle}{\sqrt{2}},
$$

where the left factor belongs to the higher-numbered qubit. Such a state is a **product state**.

## The CNOT gate

The controlled-NOT (CNOT) gate flips the **target** qubit when the **control** qubit is 1 and does nothing otherwise. Take qubit 0 as control, in $|+\rangle$, and qubit 1 as target, in $|0\rangle$, so the input is $(|00\rangle + |01\rangle)/\sqrt{2}$. The CNOT leaves $|00\rangle$ alone and changes $|01\rangle$ into $|11\rangle$:

$$
\mathrm{CNOT}\,\frac{|00\rangle + |01\rangle}{\sqrt{2}} = \frac{|00\rangle + |11\rangle}{\sqrt{2}} = |\Phi^+\rangle .
$$

This is one of the four Bell states, $|\Phi^\pm\rangle = (|00\rangle \pm |11\rangle)/\sqrt{2}$ and $|\Psi^\pm\rangle = (|01\rangle \pm |10\rangle)/\sqrt{2}$. They are orthogonal, they are all maximally entangled, and lesson 1.6 uses them as a measurement basis.

## Recognizing a product state

A pure two-qubit state is a product state exactly when $a_{00}a_{11} = a_{01}a_{10}$. For a product $(\alpha_1|0\rangle + \beta_1|1\rangle)\otimes(\alpha_0|0\rangle + \beta_0|1\rangle)$ both sides equal $\alpha_1\alpha_0\beta_1\beta_0$. For $|\Phi^+\rangle$ the left side is $1/2$ and the right side is $0$, so it is entangled.

The tempting shortcut is to count nonzero amplitudes. It fails: $(|00\rangle + |01\rangle - |10\rangle - |11\rangle)/2$ has four of them, but $a_{00}a_{11} = -1/4 = a_{01}a_{10}$, and indeed the state is $|-\rangle \otimes |+\rangle$. Nor does the opposite shortcut work, since two nonzero amplitudes are enough for entanglement.

## What each qubit looks like alone

After the CNOT, neither qubit has a pure state of its own. If you measure qubit 0 in any basis, the result is a fair coin, and the same is true of qubit 1. The Bloch vector of a qubit in this situation is inside the sphere, and for $|\Phi^+\rangle$ its length is $0$: that is the signature of being half of a maximally entangled pair. Before you apply the CNOT, predict this length, then run the circuit and read each qubit's Bloch vector at the end.

Measuring one half of the pair does tell you about the other half, though. If qubit 0 gives 0, qubit 1 will give 0 as well. Lesson 1.6 uses this correlation, together with a measurement in the Bell basis, to move a state from one place to another.
