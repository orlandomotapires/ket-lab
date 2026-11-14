import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=1)


@qml.qnode(dev)
def circuit(params):
    qml.RX(params[0], wires=0)
    qml.RY(params[1], wires=0)
    return qml.expval(qml.PauliZ(0))


def parameter_shift(params, i):
    # Ableitung von circuit nach params[i]:
    # [f(θ + π/2) − f(θ − π/2)] / 2, wobei nur der Parameter i verschoben wird.
    return 0.0


params = np.array([0.3, 0.2])
learning_rate = 0.4
history = [[float(params[0]), float(params[1]), float(circuit(params))]]

# Gradientenabstieg: Wiederhole einige Schritte von
#   params = params - learning_rate * Gradient
# und hänge in jedem Schritt [params[0], params[1], Kosten] an history an.
