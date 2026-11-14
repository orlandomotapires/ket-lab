import pennylane as qml
from pennylane import numpy as np

# Bereits vorhanden: edges (die Kanten des Graphen) und cost_h = Summe von Z_i Z_j über die Kanten.
dev = qml.device("default.qubit", wires=5)


def layer(gamma, beta):
    # 1. Kosten: IsingZZ(gamma) auf jeder Kante.
    # 2. Mischung: RX(2 * beta) auf jedem Qubit.
    pass


@qml.qnode(dev)
def circuit(params):
    for wire in range(5):
        qml.Hadamard(wires=wire)
    for gamma, beta in params:
        layer(gamma, beta)
    return qml.expval(cost_h)


np.random.seed(0)
params = np.random.uniform(-1, 1, (1, 2), requires_grad=True)  # p = 1 Schicht
history = [float(circuit(params))]

# 3. Optimiere params (minimiere circuit) und speichere jeden Wert in history.
