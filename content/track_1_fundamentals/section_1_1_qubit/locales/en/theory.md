## From bit to qubit

A classical bit can only be in one of two values: $0$ or $1$. A **qubit** also has two reference states, written $|0\rangle$ and $|1\rangle$, but it can be in any combination of them:

$$
|\psi\rangle = \alpha|0\rangle + \beta|1\rangle
$$

The numbers $\alpha$ and $\beta$ are the **amplitudes**. They are not probabilities, but they determine the probabilities: when you measure the qubit, you get $0$ with probability $|\alpha|^2$ and $1$ with probability $|\beta|^2$. Since some outcome always happens,

$$
|\alpha|^2 + |\beta|^2 = 1
$$

## The Bloch sphere

Every single-qubit state corresponds to a point on the surface of a sphere. The north pole is $|0\rangle$ and the south pole is $|1\rangle$. On the right, the vector shows where your qubit is right now.

In this lesson the vector only visits the two poles. The other points of the sphere appear starting with the next lesson.

## The X gate

Quantum gates move the vector around the sphere. The **Pauli-X** rotates it by $180°$ around the $X$ axis:

$$
X|0\rangle = |1\rangle \qquad X|1\rangle = |0\rangle
$$

It does to the qubit what `NOT` does to a bit.

## How to use the lab

- The visualization follows the **line where the cursor is**: it shows the state of the qubit after everything that has run up to that point.
- You do not need to click "run". The state is recalculated when you stop typing.
- Feel free to experiment: apply `qc.x(0)` twice, for example, and see what happens.
