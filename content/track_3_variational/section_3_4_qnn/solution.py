# Idea: the circles cannot be separated by a low-degree function of x, so the circuit loads x in
# three layers between trainable rotations (data re-uploading), then Adam fits the weights.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=2)
# Three uploads of x add higher frequencies to the output, enough for a circular boundary.
LAYERS = 3


@qml.qnode(dev)
def circuit(weights, x):
    for layer in range(LAYERS):
        for wire in range(2):
            # Trainable rotation first, then the data: the weights change which direction x rotates.
            qml.Rot(*weights[layer, wire], wires=wire)
            qml.RX(x[:, 0], wires=wire)
            qml.RY(x[:, 1], wires=wire)
        # CNOT correlates the two qubits so that qubit 0 carries information from both.
        qml.CNOT(wires=[0, 1])
    # A last trainable rotation sets the measurement direction before reading ⟨Z⟩ on qubit 0.
    for wire in range(2):
        qml.Rot(*weights[LAYERS, wire], wires=wire)
    return qml.expval(qml.PauliZ(0))


def loss(weights):
    # Mean squared error between ⟨Z₀⟩ and the labels ±1; its sign is the predicted class.
    return np.mean((circuit(weights, X_train) - y_train) ** 2)


np.random.seed(0)
weights = np.random.uniform(0, 2 * np.pi, (LAYERS + 1, 2, 3), requires_grad=True)
optimizer = qml.AdamOptimizer(0.1)
history = [float(loss(weights))]

for epoch in range(40):
    # Each Adam step lowers the training loss; history feeds the convergence plot.
    weights = optimizer.step(loss, weights)
    history.append(float(loss(weights)))
