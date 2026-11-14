import cmath
import numpy as np

z = 3 + 4j
w = 1 - 2j
theta = np.pi / 3
a = 0.6 * np.exp(0.9j)
b = 0.8 * np.exp(1.4j)

product = z * w
modulus = abs(z)
phi = np.angle(z)
z_polar = modulus * np.exp(1j * phi)
unit = np.exp(1j * theta)
unit_modulus = abs(unit)
rel_phase = np.angle(b) - np.angle(a)
