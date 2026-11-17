# Idea: each QAOA layer is a cost phase (IsingZZ on every edge) followed by a mixer (RX on every
# qubit). Two layers, trained with Adam, push the probability toward partitions with a large cut.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=5)


def layer(gamma, beta):
    # Cost unitary: IsingZZ(γ) gives each basis state a phase set by how many edges it cuts.
    for i, j in edges:
        qml.IsingZZ(gamma, wires=[i, j])
    # Mixer unitary e^{-iβΣX}: turns those phase differences into probability differences.
    for wire in range(5):
        qml.RX(2 * beta, wires=wire)


@qml.qnode(dev)
def circuit(params):
    # Hadamards prepare |+⟩ on every qubit: all 32 partitions start with equal amplitude.
    for wire in range(5):
        qml.Hadamard(wires=wire)
    # One (γ, β) pair per layer: p = len(params) layers, 2p angles in total.
    for gamma, beta in params:
        layer(gamma, beta)
    # ⟨H_C⟩ is the Ising energy: minimizing it maximizes the expected cut.
    return qml.expval(cost_h)


np.random.seed(0)
# Shape (2, 2): p = 2 layers, since p = 1 cannot reach the ratio 0.85 on this graph.
params = np.random.uniform(-1, 1, (2, 2), requires_grad=True)
optimizer = qml.AdamOptimizer(0.1)
history = [float(circuit(params))]

for step in range(80):
    # Adam adapts the step per angle, which suits the periodic QAOA landscape.
    params = optimizer.step(circuit, params)
    history.append(float(circuit(params)))
