# Idea: expand the square (Σ a_i s_i)² into pair couplings plus a constant, enumerate the 32 states
# to find the ground states, then substitute s = 1 − 2x to get the QUBO matrix and its offset.
import itertools
import numpy as np

a = np.array([4, 5, 6, 7, 8])
n = len(a)

# Each pair appears twice in the square (a_i a_j s_i s_j and a_j a_i s_j s_i), hence the factor 2;
# the pair is stored once, above the diagonal, as the form requires.
J = np.zeros((n, n))
for i in range(n):
    for j in range(i + 1, n):
        J[i, j] = 2 * a[i] * a[j]

# The terms s_i · s_i equal 1 for any spin, so they add the constant sum(a_i²) to the energy.
constant = int(np.sum(a**2))

# Enumerating in a fixed order makes the 32 energies comparable with the QUBO later.
configs = [np.array(c) for c in itertools.product([1, -1], repeat=n)]
energies = np.array([s @ J @ s + constant for s in configs])

# The ground energy is the minimum over all states, and the ground states are every state that reaches it.
ground_energy = energies.min()
ground_states = np.array([s for s, e in zip(configs, energies) if e == ground_energy])

# With s = 1 − 2x: (S − 2 a·x)² = S² − 4S a·x + 4 (a·x)², and S = sum(a).
# Since x² = x, the linear terms land on the diagonal, and the pairs keep 2 · 4 a_i a_j = 8 a_i a_j.
S = int(np.sum(a))
Q = np.zeros((n, n))
for i in range(n):
    Q[i, i] = 4 * a[i] * (a[i] - S)
    for j in range(i + 1, n):
        Q[i, j] = 8 * a[i] * a[j]

# The term independent of x is S², the energy of x = 0 (every spin +1).
offset = S**2
