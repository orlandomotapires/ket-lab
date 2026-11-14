import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=2)
LAYERS = 3


@qml.qnode(dev)
def circuit(weights, x):
    for layer in range(LAYERS):
        for wire in range(2):
            qml.Rot(*weights[layer, wire], wires=wire)
            qml.RX(x[:, 0], wires=wire)
            qml.RY(x[:, 1], wires=wire)
        qml.CNOT(wires=[0, 1])
    for wire in range(2):
        qml.Rot(*weights[LAYERS, wire], wires=wire)
    return qml.expval(qml.PauliZ(0))


def loss(weights):
    return np.mean((circuit(weights, X_train) - y_train) ** 2)


np.random.seed(0)
weights = np.random.uniform(0, 2 * np.pi, (LAYERS + 1, 2, 3), requires_grad=True)
optimizer = qml.AdamOptimizer(0.1)
history = [float(loss(weights))]

for epoch in range(40):
    weights = optimizer.step(loss, weights)
    history.append(float(loss(weights)))
