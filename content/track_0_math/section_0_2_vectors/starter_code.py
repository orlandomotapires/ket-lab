import numpy as np

# Given data
v = np.array([1 + 1j, 1 - 1j])
a = np.array([1, 1j]) / np.sqrt(2)
b = np.array([1, 1]) / np.sqrt(2)
plus = np.array([1, 1]) / np.sqrt(2)
psi = np.array([0.6, 0.8j])
phi_plus = np.array([1, 0, 0, 1]) / np.sqrt(2)
q = np.array([1, 1, 1, 1]) / 2

# Replace each 0 with your computation
norm = 0       # norm of v
v_hat = 0      # v normalized
inner = 0      # <a|b>
prob = 0       # |<a|b>|^2
minus = 0      # |-> = (|0> - |1>)/sqrt(2) as an array
amp_plus = 0   # <+|psi>
amp_minus = 0  # <-|psi>
inner4 = 0     # <phi_plus|q> in C^4
