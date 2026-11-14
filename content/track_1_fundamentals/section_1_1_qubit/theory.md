## From bit to qubit

A classical bit is either $0$ or $1$. A **qubit** has two orthogonal basis states, $|0\rangle$ and $|1\rangle$ (the **computational basis**), and its state can be any normalized linear combination of them:

$$
|\psi\rangle = \alpha|0\rangle + \beta|1\rangle
$$

The complex numbers $\alpha$ and $\beta$ are the **amplitudes**. Measuring the qubit in the computational basis gives $0$ with probability $|\alpha|^2$ and $1$ with probability $|\beta|^2$. Some outcome must occur, so

$$
|\alpha|^2 + |\beta|^2 = 1
$$

## Normalization

Not every pair of numbers is a state. $(0.6,\ 0.8)$ is valid, since $0.36 + 0.64 = 1$. $(0.6,\ 0.6)$ is not: the sum is $0.72$. Dividing the vector by its norm, here $\sqrt{0.72}$, makes it valid. Quantum gates preserve the norm, so a circuit never produces an invalid state.

## The Bloch sphere

Every pure single-qubit state corresponds to a point on the surface of a sphere. $|0\rangle$ is the north pole and $|1\rangle$ is the south pole. The vector on the right shows the current state of your qubit. In this lesson it only visits the poles; the rest of the sphere appears from lesson 1.2.

## The X gate

Gates move the state vector on the sphere. The Pauli $X$ gate rotates it by $180°$ around the $X$ axis:

$$
X|0\rangle = |1\rangle \qquad X|1\rangle = |0\rangle
$$

On computational basis states it acts like the classical NOT.

## Global phase

Multiplying a state by $e^{i\gamma}$ changes no measurement probability, so $|\psi\rangle$ and $e^{i\gamma}|\psi\rangle$ describe the same physical state and have the same point on the Bloch sphere. The **relative** phase between $\alpha$ and $\beta$ does matter; lesson 1.3 covers it.

For this reason $Y$ and $R_x(\pi)$ take $|0\rangle$ to the same physical state as $X$: $Y|0\rangle = i|1\rangle$ and $R_x(\pi)|0\rangle = -i|1\rangle$ differ from $|1\rangle$ only by a global phase.

## In the lab

- The visualization shows the state after the line where the cursor is, that is, after every gate up to that point.
- The state is recalculated when you stop typing; there is no run button.
- Try applying `qc.x(0)` twice.
