## Two states with the same odds

The states $(|0\rangle + |1\rangle)/\sqrt2$ and $(|0\rangle - |1\rangle)/\sqrt2$ give outcome 0 half the time and outcome 1 half the time, in the computational basis. Yet they are different states, and a Hadamard gate followed by a measurement tells them apart with certainty (Track 1 does this). The difference is a minus sign on one amplitude, and a minus sign is the simplest case of a phase. To talk about phases you need amplitudes that are complex numbers.

## Arithmetic and the modulus

A complex number is $z = x + iy$ with $x, y$ real and $i^2 = -1$. Its conjugate is $z^* = x - iy$ and its **modulus** is $|z| = \sqrt{z^* z} = \sqrt{x^2 + y^2}$. Addition works on the real and imaginary parts separately; multiplication uses $i^2 = -1$:

$$
(3 + 4i)(1 - 2i) = 3 - 6i + 4i - 8i^2 = 11 - 2i.
$$

The $-8i^2$ is the term people drop or get the sign of. Python writes $i$ as `1j`, so `(3 + 4j) * (1 - 2j)` prints `(11-2j)`, and `abs(z)` is the modulus.

## Polar form

Draw $z$ as a point in the plane. Its distance from the origin is $r = |z|$ and the angle from the real axis is $\varphi$, the **phase** (or argument) of $z$:

$$
z = r\,e^{i\varphi} = r(\cos\varphi + i\sin\varphi).
$$

For $3 + 4i$ we get $r = 5$ and $\varphi = \arctan(4/3) \approx 0.927$ rad. NumPy returns it with `np.angle(z)`. Polar form is what makes products easy, because moduli multiply and phases add. Check on the example above: $|3+4i| = 5$ and $|1-2i| = \sqrt5$, so the product has modulus $5\sqrt5 \approx 11.18$, which is $\sqrt{11^2 + 2^2}$. The phases are $0.927$ and $-1.107$, and their sum $-0.180$ is the angle of $11 - 2i$.

When $r = 1$ the number sits on the unit circle. Then $|e^{i\varphi}|^2 = e^{-i\varphi}e^{i\varphi} = 1$ for every $\varphi$, so multiplying by $e^{i\varphi}$ rotates a number and never stretches it. That is why phases can enter a quantum state without disturbing the probabilities. Phases are only defined modulo $2\pi$, since $e^{i\varphi} = e^{i(\varphi + 2\pi)}$.

## Global and relative phase

A qubit state is $\alpha|0\rangle + \beta|1\rangle$ with complex amplitudes, and the computational basis gives outcome 0 with probability $|\alpha|^2$ and outcome 1 with probability $|\beta|^2$. Only the moduli appear there.

Multiply both amplitudes by the same $e^{i\gamma}$ and no probability of any measurement changes. This common factor is a **global phase**, and states that differ only by it are the same physical state. The **relative phase** $\arg\beta - \arg\alpha$ is unchanged when both amplitudes are rotated together, because the shift cancels in the difference. It is what separates the plus and minus states above, whose relative phases are $0$ and $\pi$.
