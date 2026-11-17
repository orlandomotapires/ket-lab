# Idea: the spectrum of H(s) gives the gap, and a product of short exponentials
# e^{-i H(s_k) T/n} gives the time evolution, because H barely changes within one step.
import numpy as np
from scipy.linalg import expm

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=float)
Z = np.array([[1, 0], [0, -1]], dtype=float)


def on(op, q):
    factors = [I2, I2, I2]
    factors[q] = op
    return np.kron(factors[2], np.kron(factors[1], factors[0]))


H_B = -(on(X, 0) + on(X, 1) + on(X, 2))
H_P = (
    (1 / 3) * on(Z, 0) + (2 / 3) * on(Z, 1) + 1.0 * on(Z, 2)
    + (1 / 6) * on(Z, 0) @ on(Z, 1)
    + (1 / 4) * on(Z, 0) @ on(Z, 2)
    + (1 / 2) * on(Z, 1) @ on(Z, 2)
)

s_grid = np.linspace(0, 1, 101)
T_values = [1, 10, 100, 500]
n_steps = 400


def H(s):
    return (1 - s) * H_B + s * H_P


# eigvalsh returns the eigenvalues of a Hermitian matrix in ascending order, so the
# two lowest are the first two entries; their difference is the gap that matters
# (the gap to the ground state, not between higher levels).
gaps = []
for s in s_grid:
    energies = np.linalg.eigvalsh(H(s))
    gaps.append(energies[1] - energies[0])

# The adiabatic condition is controlled by the smallest gap over the whole sweep.
i_min = int(np.argmin(gaps))
min_gap = gaps[i_min]
s_at_min = s_grid[i_min]

# |110> is the ground state of H_P. In Qiskit's order that is the basis index 0b110 = 6.
target = 6

success = []
for T in T_values:
    # Start in the ground state of H_B, which is the uniform superposition.
    psi = np.ones(8, dtype=complex) / np.sqrt(8)
    dt = T / n_steps
    for k in range(n_steps):
        # Midpoint rule: H is evaluated halfway through the step, so the error is second order in dt.
        s = (k + 0.5) / n_steps
        # Each factor is unitary, so the state stays normalized.
        psi = expm(-1j * H(s) * dt) @ psi
    success.append(abs(psi[target]) ** 2)
