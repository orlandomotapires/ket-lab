# Idea: a cut edge has s_i s_j = -1, so with J_ij = +w_ij the energy E = sum w s_i s_j is lowest when
# heavy edges are cut. Cut value = sum over edges of w (1 - s_i s_j) / 2 = (W - E) / 2, W = sum of weights.
import itertools
import numpy as np

n = 5
W = sum(edges.values())

# The couplings are the weights themselves and positive: aligned neighbors cost energy (antiferromagnetic).
J_cut = np.zeros((n, n))
for (i, j), w in edges.items():
    J_cut[i, j] = w


def cut_from_energy(E):
    # An edge contributes w when cut (s_i s_j = -1) and 0 when not, so E = W - 2 cut.
    return (W - E) / 2


# With s = 1 - 2x, s_i s_j = 1 - 2x_i - 2x_j + 4 x_i x_j: the pair term goes to Q_ij and the linear
# terms land on the diagonal of both endpoints; the constant is W.
Q_cut = np.zeros((n, n))
for (i, j), w in edges.items():
    Q_cut[i, j] = 4 * w
    Q_cut[i, i] -= 2 * w
    Q_cut[j, j] -= 2 * w
offset_cut = W

# Enumerating all 32 colorings gives the lowest energy and every state that reaches it.
configs = [np.array(c) for c in itertools.product([1, -1], repeat=n)]
energy = [s @ J_cut @ s for s in configs]
lowest = min(energy)
optimal = [s for s, e in zip(configs, energy) if e == lowest]

best_cut = cut_from_energy(lowest)
# Every optimal cut appears with its mirror image, so the count of colorings is twice the count of cuts.
n_optimal = len(optimal)
best_spins = optimal[0]
