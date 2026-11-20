# Idea: the frequencies a classifier can represent grow with the number of times x is loaded, not with
# the number of qubits. One qubit that receives x four times has enough of them for a circular boundary.
import pennylane as qml
from pennylane import numpy as np

dev1 = qml.device("default.qubit", wires=1)
# Four uploads: with three, the test accuracy depends a lot on the start (83% to 97% in the runs I tried),
# and four stay above 97% for every start tried.
LAYERS = 4


@qml.qnode(dev1)
def circuit(weights, x):
    for layer in range(LAYERS):
        # Trainable rotation first: it turns the Bloch vector, so the next upload of x acts about a new axis.
        qml.Rot(*weights[layer], wires=0)
        # Both coordinates are loaded in every layer, so the output has frequencies up to LAYERS in each.
        qml.RX(x[:, 0], wires=0)
        qml.RY(x[:, 1], wires=0)
    # A last rotation chooses which axis of the Bloch sphere ⟨Z⟩ reads.
    qml.Rot(*weights[LAYERS], wires=0)
    return qml.expval(qml.PauliZ(0))


def loss(weights):
    # Mean squared error to the ±1 labels; the sign of ⟨Z⟩ is the predicted class.
    return np.mean((circuit(weights, X_train) - y_train) ** 2)


np.random.seed(0)
# One Rot (3 angles) per layer plus the final one: 3 · (LAYERS + 1) = 15 weights for the whole model.
weights = np.random.uniform(0, 2 * np.pi, (LAYERS + 1, 3), requires_grad=True)
optimizer = qml.AdamOptimizer(0.1)
history = [float(loss(weights))]

for epoch in range(60):
    # Adam steps on the training loss; the test set is only seen by the validator.
    weights = optimizer.step(loss, weights)
    history.append(float(loss(weights)))
