# Idea: Python's complex type does all the arithmetic. The modulus and the phase are the polar
# coordinates (r, φ) of z, and a relative phase is a difference of two phases.
import cmath
import numpy as np

z = 3 + 4j
w = 1 - 2j
theta = np.pi / 3
a = 0.6 * np.exp(0.9j)
b = 0.8 * np.exp(1.4j)

# Multiplication uses i² = -1; Python applies it automatically to 1j.
product = z * w
# |z| = √(z* z) = √(3² + 4²) = 5, the distance from the origin.
modulus = abs(z)
# The argument φ is the angle from the real axis, arctan(4/3) ≈ 0.927 rad.
phi = np.angle(z)
# r·e^{iφ} gives back z: the polar form is the same number written with (r, φ).
z_polar = modulus * np.exp(1j * phi)
# e^{iθ} is a point on the unit circle, a pure rotation by θ.
unit = np.exp(1j * theta)
# |e^{iθ}|² = e^{-iθ} e^{iθ} = 1, so the modulus is 1 for every θ.
unit_modulus = abs(unit)
# Relative phase of the amplitudes: arg(b) − arg(a). A common factor e^{iγ} cancels in this difference.
rel_phase = np.angle(b) - np.angle(a)
