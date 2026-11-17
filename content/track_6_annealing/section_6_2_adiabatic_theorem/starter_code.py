import numpy as np
from scipy.linalg import expm

# Single-qubit matrices and a helper that puts one of them on qubit q of three.
# Qiskit order: qubit 0 is the rightmost factor of the Kronecker product.
I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=float)
Z = np.array([[1, 0], [0, -1]], dtype=float)


def on(op, q):
    factors = [I2, I2, I2]
    factors[q] = op
    return np.kron(factors[2], np.kron(factors[1], factors[0]))


# Driver and problem Hamiltonians of the three-qubit number-partitioning instance.
H_B = -(on(X, 0) + on(X, 1) + on(X, 2))
H_P = (
    (1 / 3) * on(Z, 0) + (2 / 3) * on(Z, 1) + 1.0 * on(Z, 2)
    + (1 / 6) * on(Z, 0) @ on(Z, 1)
    + (1 / 4) * on(Z, 0) @ on(Z, 2)
    + (1 / 2) * on(Z, 1) @ on(Z, 2)
)

# Grid of the interpolation parameter, total times to try, steps per evolution.
s_grid = np.linspace(0, 1, 101)
T_values = [1, 10, 100, 500]
n_steps = 400

# Gap between the two lowest eigenvalues of H(s) = (1 - s) H_B + s H_P, for each s in s_grid.
gaps = []

# Smallest gap on the grid, and the value of s where it occurs.
min_gap = 0.0
s_at_min = 0.0

# Probability of finding |110> at the end of the evolution, one value per entry of T_values.
# Start from |+++> and use n_steps short steps, with H evaluated at the middle of each step.
success = []
