import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=5)


def layer(gamma, beta):
    for i, j in edges:
        qml.IsingZZ(gamma, wires=[i, j])
    for wire in range(5):
        qml.RX(2 * beta, wires=wire)


@qml.qnode(dev)
def circuit(params):
    for wire in range(5):
        qml.Hadamard(wires=wire)
    for gamma, beta in params:
        layer(gamma, beta)
    return qml.expval(cost_h)


np.random.seed(0)
params = np.random.uniform(-1, 1, (2, 2), requires_grad=True)
optimizer = qml.AdamOptimizer(0.1)
history = [float(circuit(params))]

for step in range(80):
    params = optimizer.step(circuit, params)
    history.append(float(circuit(params)))
