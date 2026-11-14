## Complex numbers

A complex number is $z = x + iy$ with $x, y$ real and $i^2 = -1$. Its **complex conjugate** is $z^* = x - iy$, and its **modulus** is

$$
|z| = \sqrt{z^* z} = \sqrt{x^2 + y^2}.
$$

Addition acts on real and imaginary parts separately. Multiplication uses $i^2 = -1$:

$$
(3 + 4i)(1 - 2i) = 3 - 6i + 4i - 8i^2 = 11 - 2i.
$$

Python writes $i$ as `1j`, so `(3 + 4j) * (1 - 2j)` gives `(11-2j)`. `abs(z)` returns the modulus and `np.angle(z)` (or `cmath.phase(z)`) the argument.

## Polar form

Every nonzero $z$ is a point in the plane at distance $r = |z|$ from the origin and angle $\varphi$ from the real axis:

$$
z = r\,e^{i\varphi} = r(\cos\varphi + i\sin\varphi).
$$

The angle $\varphi$ is the **phase** (argument) of $z$. For $3 + 4i$, $r = 5$ and $\varphi = \arctan(4/3) \approx 0.927$ rad. In polar form, products are simple: moduli multiply and phases add,

$$
r_1 e^{i\varphi_1}\, r_2 e^{i\varphi_2} = r_1 r_2\, e^{i(\varphi_1 + \varphi_2)}.
$$

## Why the modulus of $e^{i\varphi}$ is 1

$$
|e^{i\varphi}|^2 = (e^{i\varphi})^* e^{i\varphi} = e^{-i\varphi} e^{i\varphi} = e^0 = 1.
$$

Equivalently, $|\cos\varphi + i\sin\varphi|^2 = \cos^2\varphi + \sin^2\varphi = 1$. Multiplying by $e^{i\varphi}$ rotates a number in the plane and leaves its modulus unchanged. This is the property that lets phases appear in quantum states without changing probabilities.

## Global and relative phase

A qubit state is $\alpha|0\rangle + \beta|1\rangle$ with complex amplitudes $\alpha, \beta$. Measuring in the computational basis gives outcome 0 with probability $|\alpha|^2$ and outcome 1 with probability $|\beta|^2$, so only the moduli matter there.

Multiplying both amplitudes by the same $e^{i\gamma}$ is a **global phase**. It changes no probability for any measurement, and states that differ by it are physically the same. The **relative phase** is the difference $\arg\beta - \arg\alpha$. It cannot be removed, and it decides, for example, whether $(|0\rangle + |1\rangle)/\sqrt2$ or $(|0\rangle - |1\rangle)/\sqrt2$ is prepared. Track 1 shows how a Hadamard gate turns a relative phase into a measurable difference.

Phases are defined modulo $2\pi$: $e^{i\varphi} = e^{i(\varphi + 2\pi)}$.
