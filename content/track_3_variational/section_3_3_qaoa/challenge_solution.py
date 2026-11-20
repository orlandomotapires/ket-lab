# Idea: on a ring every vertex has two neighbours, so one layer sees only the edges next to a given
# edge and cuts 3/4 of them on average at best; each extra layer reaches one vertex further and the
# best ratio becomes (2p + 1)/(2p + 2). We train p = 1 and p = 2 and keep the best of a few starts,
# because the p = 2 landscape has poor local optima.
import pennylane as qml
from pennylane import numpy as np

dev8 = qml.device("default.qubit", wires=8)


@qml.qnode(dev8)
def circuit(params):
    # |+⟩ on every vertex: the 256 colorings start with equal amplitude.
    for wire in range(8):
        qml.Hadamard(wires=wire)
    for gamma, beta in params:
        # Cost phase on each of the 8 ring edges, then the mixer on every qubit, as in the mission.
        for i, j in ring_edges:
            qml.IsingZZ(gamma, wires=[i, j])
        for wire in range(8):
            qml.RX(2 * beta, wires=wire)
    return qml.expval(ring_cost_h)


def ratio_of(params):
    # Each cut edge contributes -1 to ⟨ZZ⟩ and each uncut edge +1, so the cut is (8 - ⟨H⟩)/2;
    # an 8-ring can cut all 8 edges, which sets the denominator.
    return float((8 - circuit(params)) / 2 / 8)


def train(p, seed, steps=60):
    # A different seed gives a different start; Adam adapts the step to each angle.
    np.random.seed(seed)
    params = np.random.uniform(-1, 1, (p, 2), requires_grad=True)
    optimizer = qml.AdamOptimizer(0.1)
    for _ in range(steps):
        params = optimizer.step(circuit, params)
    return params


def best_of(p, seeds):
    # Keeping the best of several starts guards against a start that lands in a local optimum.
    runs = [train(p, seed) for seed in seeds]
    return max(runs, key=ratio_of)


angles_p1 = best_of(1, [0])
angles_p2 = best_of(2, [0, 1, 2])
# The ratios are computed from the circuit, so the check can compare them with its own values.
ratio_p1 = ratio_of(angles_p1)
ratio_p2 = ratio_of(angles_p2)
print(ratio_p1, ratio_p2)
# The lab draws the QNode `circuit` at `params`: show the trained two-layer ring.
params = angles_p2
