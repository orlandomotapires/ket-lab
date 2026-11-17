import cmath
import numpy as np

# Given data
z = 3 + 4j
w = 1 - 2j
theta = np.pi / 3
a = 0.6 * np.exp(0.9j)  # amplitude of |0>
b = 0.8 * np.exp(1.4j)  # amplitude of |1>

# Replace each 0 with your computation
product = 0       # z * w
modulus = 0       # |z|
phi = 0           # argument (phase) of z
z_polar = 0       # modulus * e^{i phi}, must equal z
unit = 0          # e^{i theta}
unit_modulus = 0  # |unit|
rel_phase = 0     # phase of b minus phase of a
