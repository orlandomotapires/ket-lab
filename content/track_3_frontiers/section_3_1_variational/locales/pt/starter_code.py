import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=1)


@qml.qnode(dev)
def circuit(params):
    qml.RX(params[0], wires=0)
    qml.RY(params[1], wires=0)
    return qml.expval(qml.PauliZ(0))


def parameter_shift(params, i):
    # Derivada de circuit em relação a params[i]:
    # [f(θ + π/2) − f(θ − π/2)] / 2, deslocando só o parâmetro i.
    return 0.0


params = np.array([0.3, 0.2])
learning_rate = 0.4
history = [[float(params[0]), float(params[1]), float(circuit(params))]]

# Gradiente descendente: repita alguns passos de
#   params = params - learning_rate * gradiente
# e acrescente [params[0], params[1], custo] a history em cada passo.
