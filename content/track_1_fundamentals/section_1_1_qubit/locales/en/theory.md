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

## Normalization

Not every pair of numbers is a state. The amplitudes must satisfy $|\alpha|^2 + |\beta|^2 = 1$. For example, $(0.6,\ 0.8)$ is a valid state, since $0.36 + 0.64 = 1$. But $(0.6,\ 0.6)$ is not: the sum is $0.72$. To make it valid, divide the vector by its norm (here, $\sqrt{0.72}$). Quantum gates preserve this sum, so a circuit never produces a vector outside the sphere.

## Global phase

Multiplying the whole state by $e^{i\gamma}$ changes no probability and no outcome of any possible measurement: $|\psi\rangle$ and $e^{i\gamma}|\psi\rangle$ are physically the same state, and the Bloch sphere draws them at the same point. What matters is the **relative** phase between $\alpha$ and $\beta$, the subject of lesson 1.3.

That is why $Y$ and $R_x(\pi)$ take $|0\rangle$ to the same physical state that $X$ does: the results differ only by a global phase ($Y|0\rangle = i|1\rangle$ and $R_x(\pi)|0\rangle = -i|1\rangle$).

## How to use the lab

- The visualization follows the **line where the cursor is**: it shows the state of the qubit after everything that has run up to that point.
- You do not need to click "run". The state is recalculated when you stop typing.
- Feel free to experiment: apply `qc.x(0)` twice, for example, and see what happens.
