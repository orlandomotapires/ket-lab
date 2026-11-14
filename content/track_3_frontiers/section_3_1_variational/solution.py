import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=1)


@qml.qnode(dev)
def circuit(params):
    qml.RX(params[0], wires=0)
    qml.RY(params[1], wires=0)
    return qml.expval(qml.PauliZ(0))


def parameter_shift(params, i):
    shift = np.zeros_like(params)
    shift[i] = np.pi / 2
    return (circuit(params + shift) - circuit(params - shift)) / 2


params = np.array([0.3, 0.2])
learning_rate = 0.4
history = [[float(params[0]), float(params[1]), float(circuit(params))]]

for step in range(60):
    gradient = np.array([parameter_shift(params, i) for i in range(len(params))])
    params = params - learning_rate * gradient
    history.append([float(params[0]), float(params[1]), float(circuit(params))])
