import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=1)


@qml.qnode(dev)
def circuit(params):
    qml.RX(params[0], wires=0)
    qml.RY(params[1], wires=0)
    return qml.expval(qml.PauliZ(0))


def parameter_shift(params, i):
    # Parameter-shift rule for params[i]:
    # [f(θ + π/2) − f(θ − π/2)] / 2, shifting only params[i].
    return 0.0


params = np.array([0.3, 0.2])
learning_rate = 0.4
history = [[float(params[0]), float(params[1]), float(circuit(params))]]

# Gradient descent: repeat
#   params = params - learning_rate * gradient
# and append [params[0], params[1], cost] to history after each step.
