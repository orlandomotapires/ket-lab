## Circuits with parameters

So far, every gate had a fixed angle. A **variational circuit** has adjustable angles $\vec\theta$, and the result of a measurement becomes a function of them:

$$
f(\vec\theta) = \langle \psi(\vec\theta) |\, O \,| \psi(\vec\theta) \rangle
$$

where $O$ is an observable, such as $Z$. A classical computer chooses the angles, the quantum one evaluates $f$, and the classical one adjusts the angles to minimize $f$. This hybrid loop is the basis of VQE, QAOA and the quantum neural networks in the next lessons.

The circuit with parameters is called an **ansatz**. A good ansatz reaches enough states to contain the answer (**expressibility**) without being so large that it becomes impossible to train.

## PennyLane

In this track the circuits are written in PennyLane, which computes gradients of quantum circuits:

- `qml.device("default.qubit", wires=1)` creates a 1-qubit simulator;
- `@qml.qnode(dev)` turns a Python function into an executable circuit, the **QNode**;
- the function applies gates, such as `qml.RX(θ, wires=0)`, and returns a measurement, such as `qml.expval(qml.PauliZ(0))`;
- `from pennylane import numpy as np` provides a NumPy that PennyLane knows how to differentiate.

The platform shows qubits in the same order as the other tracks: qubit 0 is on the right in the labels.

## The parameter-shift rule

To minimize $f$, you need the gradient. On a real quantum computer you cannot "look inside" the circuit, and finite differences, $[f(\theta + \epsilon) - f(\theta)]/\epsilon$, get lost in measurement noise. For rotation gates such as $R_X$ and $R_Y$, however, the derivative is exact from two runs of the circuit itself:

$$
\frac{\partial f}{\partial \theta_i} = \frac{f\!\left(\theta_i + \frac{\pi}{2}\right) - f\!\left(\theta_i - \frac{\pi}{2}\right)}{2}
$$

with the other parameters fixed. The shifts are large, $\pm\pi/2$, so measurement noise matters little. This is the **parameter-shift rule**.

## Gradient descent

With the gradient, each step moves a little in the downhill direction:

$$
\vec\theta \;\leftarrow\; \vec\theta - \eta\, \nabla f(\vec\theta)
$$

The **learning rate** $\eta$ controls the step size: too small makes training slow; too large makes the optimizer jump over the minimum.

## In this lab

The cost is $\langle Z\rangle$ after $R_X(\theta_0)$ and $R_Y(\theta_1)$, which equals $\cos\theta_0 \cos\theta_1$. The minimum, $-1$, is the south pole of the Bloch sphere.

- The **Landscape** tab shows the cost for all angles, with the trajectory of your optimizer.
- The **Convergence** tab shows the cost step by step.
- The **Bloch spheres** show the state with the final parameters.

Since training takes a few moments, the code runs when you click **Run** or press Ctrl+Enter.
