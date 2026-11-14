import pennylane as qml
from pennylane import numpy as np

# Already available: edges (the graph's edges) and cost_h = sum of Z_i Z_j over the edges.
dev = qml.device("default.qubit", wires=5)


def layer(gamma, beta):
    # 1. Cost: IsingZZ(gamma) on each edge.
    # 2. Mixer: RX(2 * beta) on each qubit.
    pass


@qml.qnode(dev)
def circuit(params):
    for wire in range(5):
        qml.Hadamard(wires=wire)
    for gamma, beta in params:
        layer(gamma, beta)
    return qml.expval(cost_h)


np.random.seed(0)
params = np.random.uniform(-1, 1, (1, 2), requires_grad=True)  # p = 1 layer
history = [float(circuit(params))]

# 3. Optimize params (minimize circuit) and store each value in history.
