import pennylane as qml
from pennylane import numpy as np

# Bereits vorhanden: X_train (80 2D-Punkte, Form (80, 2)) und y_train (Labels +1 oder −1).
dev = qml.device("default.qubit", wires=2)
LAYERS = 1


@qml.qnode(dev)
def circuit(weights, x):
    # x hat die Form (N, 2): Der Schaltkreis verarbeitet alle Punkte auf einmal.
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
history = [float(loss(weights))]

# Trainiere weights mit einem Optimierer und speichere den Verlust jeder Epoche in history.
