import numpy as np

# Readout error of one qubit: A[i, j] = P(read i | true j).
A = np.array([[0.95, 0.10], [0.05, 0.90]])
# The true state has P(0) = 0.8 and P(1) = 0.2, so the exact ⟨Z⟩ is 0.6. These are the measured frequencies.
p_meas = A @ np.array([0.8, 0.2])


def _ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def noisy_expectation(scale):
    """⟨Z⟩ after the circuit G = R_y(0.9) on |0⟩, with noise scaled by `scale` (1, 3, 5, ...).

    The circuit is folded as G (G† G)^k with scale = 2k + 1. After every gate the qubit suffers
    depolarizing noise (p = 0.05) and amplitude damping (γ = 0.02). The ideal value is cos(0.9)."""
    if scale < 1 or int(scale) != scale or int(scale) % 2 == 0:
        raise ValueError("scale must be an odd integer: 1, 3, 5, ...")
    gate = _ry(0.9)
    gates = [gate] + [gate.conj().T, gate] * ((int(scale) - 1) // 2)
    k0 = np.diag([1, np.sqrt(1 - 0.02)]).astype(complex)
    k1 = np.array([[0, np.sqrt(0.02)], [0, 0]], dtype=complex)
    rho = np.diag([1, 0]).astype(complex)
    for u in gates:
        rho = u @ rho @ u.conj().T
        rho = 0.95 * rho + 0.05 * np.eye(2) / 2
        rho = k0 @ rho @ k0.conj().T + k1 @ rho @ k1.conj().T
    return float(np.real(rho[0, 0] - rho[1, 1]))


# A deeper circuit with much stronger noise per gate (depolarizing p = 0.15, amplitude damping
# γ = 0.05), for the challenge. deep_expectation(s) is the exact value with infinitely many shots.
def deep_expectation(scale):
    if scale < 1 or int(scale) != scale or int(scale) % 2 == 0:
        raise ValueError("scale must be an odd integer: 1, 3, 5, ...")
    gate = _ry(0.9)
    gates = [gate] + [gate.conj().T, gate] * ((int(scale) - 1) // 2)
    k0 = np.diag([1, np.sqrt(1 - 0.05)]).astype(complex)
    k1 = np.array([[0, np.sqrt(0.05)], [0, 0]], dtype=complex)
    rho = np.diag([1, 0]).astype(complex)
    for u in gates:
        rho = u @ rho @ u.conj().T
        rho = 0.85 * rho + 0.15 * np.eye(2) / 2
        rho = k0 @ rho @ k0.conj().T + k1 @ rho @ k1.conj().T
    return float(np.real(rho[0, 0] - rho[1, 1]))


# What the device returned at the scales 1, 3, 5: the exact values plus shot noise of size sigma.
ideal = float(np.cos(0.9))
sigma = 0.02
_rng = np.random.default_rng(9)
measured = [round(deep_expectation(s) + float(_rng.normal(0, sigma)), 4) for s in (1, 3, 5)]
