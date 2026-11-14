import pennylane as qml
from pennylane import numpy as np

# Já disponíveis: edges (as arestas do grafo) e cost_h = soma de Z_i Z_j nas arestas.
dev = qml.device("default.qubit", wires=5)


def layer(gamma, beta):
    # 1. Custo: IsingZZ(gamma) em cada aresta.
    # 2. Mistura: RX(2 * beta) em cada qubit.
    pass


@qml.qnode(dev)
def circuit(params):
    for wire in range(5):
        qml.Hadamard(wires=wire)
    for gamma, beta in params:
        layer(gamma, beta)
    return qml.expval(cost_h)


np.random.seed(0)
params = np.random.uniform(-1, 1, (1, 2), requires_grad=True)  # p = 1 camada
history = [float(circuit(params))]

# 3. Otimize params (minimize circuit) e guarde cada valor em history.
