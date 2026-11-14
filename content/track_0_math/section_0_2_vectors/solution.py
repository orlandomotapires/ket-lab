import numpy as np

v = np.array([1 + 1j, 1 - 1j])
a = np.array([1, 1j]) / np.sqrt(2)
b = np.array([1, 1]) / np.sqrt(2)
plus = np.array([1, 1]) / np.sqrt(2)
psi = np.array([0.6, 0.8j])
phi_plus = np.array([1, 0, 0, 1]) / np.sqrt(2)
q = np.array([1, 1, 1, 1]) / 2

norm = np.linalg.norm(v)
v_hat = v / norm
inner = np.vdot(a, b)
prob = abs(inner) ** 2
minus = np.array([1, -1]) / np.sqrt(2)
amp_plus = np.vdot(plus, psi)
amp_minus = np.vdot(minus, psi)
inner4 = np.vdot(phi_plus, q)
