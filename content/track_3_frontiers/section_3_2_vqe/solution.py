import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=4)


@qml.qnode(dev)
def circuit(theta):
    qml.BasisState(hf_state, wires=[0, 1, 2, 3])
    qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])
    return qml.expval(H)


theta = np.array(0.0, requires_grad=True)
optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
energies = [float(circuit(theta))]

for step in range(40):
    theta = optimizer.step(circuit, theta)
    energies.append(float(circuit(theta)))

energy = energies[-1]
