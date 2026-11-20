# Idea: near an avoided crossing the whole sweep reduces to a two-level problem, and the chance of
# jumping to the upper level depends only on Δ²/v, where Δ is the gap at the crossing and v the speed
# at which the two uncoupled energies approach each other. Simulating the sweep and comparing it
# with exp(−πΔ²/(2v)) ties the speed of an annealing schedule to the gap quantitatively.
import numpy as np
from scipy.linalg import expm

X = np.array([[0, 1], [1, 0]], dtype=float)
Z = np.array([[1, 0], [0, -1]], dtype=float)


def landau_zener(v, delta):
    # The probability of ending in the excited level, with ħ = 1.
    return float(np.exp(-np.pi * delta**2 / (2 * v)))


def sweep_probability(v, delta, T, n_steps):
    def ham(t):
        # The uncoupled levels are ±v·t/2, so their difference changes at rate v; the coupling Δ/2
        # opens a gap of exactly Δ at t = 0.
        return (v * t / 2) * Z + (delta / 2) * X

    dt = 2 * T / n_steps
    # Start in the ground state of H(−T), which is almost |0⟩ but not exactly.
    psi = np.linalg.eigh(ham(-T))[1][:, 0].astype(complex)
    for k in range(n_steps):
        # Midpoint rule, as in the mission: H is nearly constant within one short step.
        t = -T + (k + 0.5) * dt
        psi = expm(-1j * ham(t) * dt) @ psi
    # Read out in the excited eigenstate of H(T), not in |0⟩: the two differ by a small angle at finite T.
    excited = np.linalg.eigh(ham(T))[1][:, 1]
    return float(abs(excited.conj() @ psi) ** 2)


rates = [0.5, 1, 2, 4]
delta, T_sweep, steps = 1.0, 20, 2000
simulated = [sweep_probability(v, delta, T_sweep, steps) for v in rates]
predicted = [landau_zener(v, delta) for v in rates]
print(simulated, predicted)
