## Turning a circuit into a function

Take one qubit, rotate it about x by an angle $\theta$, and measure $Z$. Repeating the run many times and averaging the outcomes gives $\langle Z\rangle = \cos\theta$: $+1$ at $\theta = 0$, $0$ at $\pi/2$, $-1$ at $\pi$. The circuit has become a function of its angle, and finding the angle that makes it smallest is an optimization problem. Variational algorithms are built on this idea, with more qubits and more angles.

In general a circuit with adjustable angles $\vec\theta$ prepares $|\psi(\vec\theta)\rangle$, and an observable $O$ gives the **expectation value**, the average of the measurement outcomes:

$$
f(\vec\theta) = \langle \psi(\vec\theta) |\, O \,| \psi(\vec\theta) \rangle .
$$

A classical optimizer proposes angles, the quantum computer evaluates $f$, and the optimizer updates the angles to lower it. VQE, QAOA and the classifier of the next lessons all run this loop. The parameterized circuit is called the **ansatz**: it has to be rich enough to contain the answer and small enough to train. For $a|0\rangle + b|1\rangle$ and $O = Z$, $f = |a|^2 - |b|^2$.

The circuits of this track are written in PennyLane. A device such as `qml.device("default.qubit", wires=1)` is a simulator, `@qml.qnode(dev)` turns a Python function that applies gates and returns `qml.expval(...)` into a circuit you can call like a function, and `from pennylane import numpy as np` gives a NumPy whose arrays PennyLane can differentiate.

## The gradient from two runs

Gradient descent needs $\nabla f$. On hardware the circuit is a black box that returns noisy averages, and a finite difference $[f(\theta+\epsilon)-f(\theta)]/\epsilon$ with small $\epsilon$ divides that noise by $\epsilon$. The **parameter-shift rule** avoids this: it gives the exact derivative from two runs of the same circuit, with the angle moved by $\pm\pi/2$.

It holds when $\theta_i$ sits in a gate $e^{-i\theta_i G/2}$ with $G$ a Pauli operator (or any operator with eigenvalues $\pm 1$), which covers $R_X$, $R_Y$, $R_Z$ and IsingZZ. All other parameters stay fixed below.

Since $G^2 = I$, the gate expands exactly as

$$
e^{-i\theta G/2} = \cos\tfrac{\theta}{2}\, I - i \sin\tfrac{\theta}{2}\, G .
$$

The amplitudes after the gate are linear in $\cos\frac{\theta}{2}$ and $\sin\frac{\theta}{2}$, and the expectation value is quadratic in the amplitudes, so it contains $\cos^2\frac{\theta}{2}$, $\sin^2\frac{\theta}{2}$ and $\sin\frac{\theta}{2}\cos\frac{\theta}{2}$. The half-angle identities turn these into a constant, $\cos\theta$ and $\sin\theta$:

$$
f(\theta) = a\cos\theta + b\sin\theta + c .
$$

With $\cos(\theta\pm\frac{\pi}{2}) = \mp\sin\theta$ and $\sin(\theta\pm\frac{\pi}{2}) = \pm\cos\theta$,

$$
\frac{f\!\left(\theta + \frac{\pi}{2}\right) - f\!\left(\theta - \frac{\pi}{2}\right)}{2} = -a\sin\theta + b\cos\theta = \frac{\partial f}{\partial \theta}.
$$

The constant $c$ cancels and nothing was approximated, so the result holds for any $\theta$, not only for small shifts. The two runs are $\pi$ apart, which keeps the shot noise on each small next to their difference.

Check it on the simplest case. For $R_X(\theta)|0\rangle$ and $O = Z$, $f = \cos\theta$, and the rule gives $[\cos(\theta+\frac{\pi}{2}) - \cos(\theta-\frac{\pi}{2})]/2 = [-\sin\theta - \sin\theta]/2 = -\sin\theta$, the true derivative. Easy to get wrong when you code it: the shift is $\pi/2$ and the factor is $\tfrac12$, not a small $\epsilon$ and not $1/(2\epsilon)$.

## Gradient descent

Each step moves the parameters against the gradient, $\vec\theta \leftarrow \vec\theta - \eta\, \nabla f(\vec\theta)$. A small learning rate $\eta$ is slow, and a large one overshoots the minimum.

The lab applies $R_X(\theta_0)$ and then $R_Y(\theta_1)$ to $|0\rangle$, so $f = \cos\theta_0\cos\theta_1$. At $\vec\theta = (0.3, 0.2)$ the gradient is $(-\sin 0.3\cos 0.2,\; -\cos 0.3\sin 0.2) \approx (-0.290, -0.190)$. With $\eta = 0.4$ one step gives $\vec\theta \approx (0.416, 0.276)$, and the cost drops from $0.936$ to $0.880$. We start close to a maximum, where the gradient is small, so the first steps are short and then grow as the slope steepens.

Before you run it, predict which of the two angles ends near zero and which near $\pi$, and where the Bloch vector finishes. Then compare with the Bloch view. Run it with about 60 steps, and also watch the cost on the way: it passes through 0 (the equator) after about six steps.
