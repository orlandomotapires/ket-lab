import pennylane as qml
from pennylane import numpy as np

# Already defined: edges (the graph's edges) and cost_h, the sum of Z_i Z_j over the edges.
dev = qml.device("default.qubit", wires=5)


def layer(gamma, beta):
    # 1. Cost unitary: IsingZZ(gamma) on each edge.
    # 2. Mixer unitary: RX(2 * beta) on each qubit.
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

# 3. Minimize circuit(params) over params and append each value to history.
