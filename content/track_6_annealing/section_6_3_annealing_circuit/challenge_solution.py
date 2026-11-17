# Idea: the linear anneal wastes steps where the gap is large. Move through s at a speed proportional
# to gap(s)^2 (the local adiabatic schedule): slow near s = 0.95, fast elsewhere. With the steps
# fixed at dt = 1.2, fewer steps are needed and the circuit gets much shorter.
import numpy as np
from qiskit import QuantumCircuit

h = [1 / 3, 2 / 3, 1]
J = {(0, 1): 1 / 6, (0, 2): 1 / 4, (1, 2): 1 / 2}

# The 8 x 8 matrices of lesson 6.2, with qubit 0 as the rightmost factor.
I2, X, Z = np.eye(2), np.array([[0, 1], [1, 0]]), np.diag([1, -1])


def on(op, q):
    f = [I2, I2, I2]
    f[q] = op
    return np.kron(f[2], np.kron(f[1], f[0]))


H_B = -(on(X, 0) + on(X, 1) + on(X, 2))
H_P = sum(h[i] * on(Z, i) for i in range(3)) + sum(c * on(Z, i) @ on(Z, j) for (i, j), c in J.items())

# The gap to the first excited state, on a fine grid of s.
grid = np.linspace(0, 1, 1001)
gap = np.array([np.diff(np.linalg.eigvalsh((1 - s) * H_B + s * H_P)[:2])[0] for s in grid])

# Local adiabatic rule: ds/dt = c gap^2. Integrating dt = ds / (c gap^2) gives the time t(s) spent up
# to each s, so t(s) grows fast where the gap is small. A smaller c means a slower sweep.
c = 0.212
speed = c * gap**2
mid_speed = (speed[1:] + speed[:-1]) / 2
t = np.concatenate([[0], np.cumsum(np.diff(grid) / mid_speed)])
T = t[-1]

# Equal time steps of about 1.2 keep the Trotter error small, and s is read from t(s) at each midpoint.
p = int(round(T / 1.2))
dt = T / p
s_mid = np.interp((np.arange(p) + 0.5) * dt, t, grid)

qc = QuantumCircuit(3)
# Start in |+++>, the ground state of H_B.
qc.h([0, 1, 2])
for s in s_mid:
    # Same layers as the mission: cost with the factor 2 of rz and rzz, then the mixer with a minus sign.
    for i in range(3):
        qc.rz(2 * s * h[i] * dt, i)
    for (i, j), coupling in J.items():
        qc.rzz(2 * s * coupling * dt, i, j)
    for i in range(3):
        qc.rx(-2 * (1 - s) * dt, i)
