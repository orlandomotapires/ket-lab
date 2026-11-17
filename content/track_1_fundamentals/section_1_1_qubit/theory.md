## Two numbers instead of one bit

Suppose a device gives 0 in 36% of the runs and 1 in the other 64%. A qubit that behaves this way is described by two numbers, 0.6 and 0.8, written as a state vector:

$$
|\psi\rangle = 0.6\,|0\rangle + 0.8\,|1\rangle
$$

The squares of the numbers are the probabilities, $0.36$ and $0.64$. The vectors $|0\rangle$ and $|1\rangle$ form the **computational basis**: the two states that a measurement tells apart with certainty. The numbers in front of them are the **amplitudes**, and in general they are complex. For $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ the measurement gives $0$ with probability $|\alpha|^2$ and $1$ with probability $|\beta|^2$, and some outcome must occur, so

$$
|\alpha|^2 + |\beta|^2 = 1 .
$$

Not every pair of numbers passes this test. $(0.6,\ 0.6)$ adds up to $0.72$, so it is not a state; dividing both numbers by $\sqrt{0.72} \approx 0.849$ gives $(0.707,\ 0.707)$, which is. Gates never leave the set of valid states, because they preserve this sum.

## The Bloch sphere

Every pure state of one qubit is a point on a sphere. $|0\rangle$ sits at the north pole and $|1\rangle$ at the south pole, and two angles fix the rest, up to a global phase (defined below):

$$
|\psi\rangle = \cos\frac{\theta}{2}\,|0\rangle + e^{i\phi}\sin\frac{\theta}{2}\,|1\rangle .
$$

$\theta$ is measured from the north pole and $\phi$ is the longitude. For $0.6|0\rangle + 0.8|1\rangle$ we need $\tan(\theta/2) = 0.8/0.6$, so $\theta/2 \approx 53.1°$ and $\theta \approx 106°$. The half angle is where people slip: $|1\rangle$ is at $\theta = \pi$, yet its amplitude uses $\sin(\pi/2) = 1$. The gate $R_y(\theta)$ takes $|0\rangle$ to the state with this $\theta$ and $\phi = 0$, which is what the challenge uses.

## The X gate

A gate moves the point on the sphere. The Pauli $X$ gate is a half turn about the $X$ axis, so it swaps the poles:

$$
X|0\rangle = |1\rangle, \qquad X|1\rangle = |0\rangle .
$$

On these two states it behaves like the classical NOT, which is all the mission needs.

## Global phase

Multiplying a state by $e^{i\gamma}$ changes no probability, so $|\psi\rangle$ and $e^{i\gamma}|\psi\rangle$ are the same physical state and the same point on the sphere. The phase between $\alpha$ and $\beta$ is a different matter and does count (lesson 1.3).

This is why $X$ is not the only gate that solves the mission. The gate $Y$ gives $Y|0\rangle = i|1\rangle$, and $R_x(\pi)|0\rangle = -i|1\rangle$. Both differ from $|1\rangle$ by a factor of modulus 1, so the validator accepts them.

## Predict, then check

Before typing anything, decide where `qc.x(0)` repeated twice leaves the vector, and where `qc.y(0)` leaves it when applied to $|0\rangle$. Then write the gates one at a time and compare.
