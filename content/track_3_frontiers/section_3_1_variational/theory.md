## Variational circuits

A **variational circuit** (or variational form) is a circuit whose gates have adjustable angles $\vec\theta$. Preparing $|\psi(\vec\theta)\rangle$ and measuring an observable $O$ gives an expectation value that is a function of the angles:

$$
f(\vec\theta) = \langle \psi(\vec\theta) |\, O \,| \psi(\vec\theta) \rangle
$$

A classical optimizer picks the angles, the quantum computer evaluates $f$, and the optimizer updates the angles to minimize $f$. VQE, QAOA and the variational classifier in the next lessons use this loop. The parameterized circuit is called an **ansatz**. It should be expressive enough to contain the solution and small enough to train.

## PennyLane

The circuits in this track are written in PennyLane.

- `qml.device("default.qubit", wires=1)` creates a one-qubit simulator.
- `@qml.qnode(dev)` turns a Python function into an executable circuit (a QNode). The function applies gates such as `qml.RX(θ, wires=0)` and returns a measurement such as `qml.expval(qml.PauliZ(0))`.
- `from pennylane import numpy as np` provides a NumPy that PennyLane can differentiate.

## The parameter-shift rule

Minimizing $f$ by gradient descent requires its gradient. On hardware the circuit is a black box, and finite differences $[f(\theta+\epsilon)-f(\theta)]/\epsilon$ with small $\epsilon$ are swamped by statistical noise. The **parameter-shift rule** gives the exact derivative from two evaluations of the same circuit.

It holds when $\theta_i$ appears in a gate $e^{-i\theta_i G/2}$ with $G$ a Pauli operator (or any operator with eigenvalues $\pm 1$), which covers $R_X$, $R_Y$, $R_Z$ and $\mathrm{IsingZZ}$. Then $f$ is a sinusoid in $\theta_i$, $f = a\cos\theta_i + b\sin\theta_i + c$, and

$$
\frac{\partial f}{\partial \theta_i} = \frac{f\!\left(\theta_i + \frac{\pi}{2}\right) - f\!\left(\theta_i - \frac{\pi}{2}\right)}{2}
$$

with all other parameters fixed. The two evaluations are far apart ($\pi$ in total), so the shot noise on each is small compared with their difference.

## Gradient descent

Each step moves the parameters against the gradient:

$$
\vec\theta \;\leftarrow\; \vec\theta - \eta\, \nabla f(\vec\theta)
$$

The learning rate $\eta$ sets the step size. If it is too small, training is slow. If it is too large, the steps overshoot the minimum.

## In the lab

The cost is $\langle Z\rangle$ after $R_X(\theta_0)$ and $R_Y(\theta_1)$, which equals $\cos\theta_0\cos\theta_1$. Its minimum, $-1$, is the south pole of the Bloch sphere.

- Landscape: the cost over all angles, with the path of your optimizer.
- Convergence: the cost at each step.
- Bloch spheres: the state for the final parameters.

Training takes a moment, so the code runs when you click Run or press Ctrl+Enter.
