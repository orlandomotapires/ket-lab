import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=4)

distances = [0.5, 0.6, 0.7, 0.8, 1.0, 1.5, 2.0]
steps = 40

thetas = []
histories = []

for d in distances:
    H = hamiltonian(d)

    @qml.qnode(dev)
    def circuit(theta):
        qml.BasisState(hf_state, wires=[0, 1, 2, 3])
        qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])
        return qml.expval(H)

    theta = np.array(0.0, requires_grad=True)
    optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
    history = [float(circuit(theta))]
    for _ in range(steps):
        theta = optimizer.step(circuit, theta)
        history.append(float(circuit(theta)))
    thetas.append(float(theta))
    histories.append(history)

energies = [history[-1] for history in histories]

# Equilibrium: vertex of the parabola through the three lowest points.
lowest = sorted(range(len(distances)), key=lambda k: energies[k])[:3]
c2, c1, c0 = np.polyfit([distances[k] for k in lowest], [energies[k] for k in lowest], 2)
r_eq = float(-c1 / (2 * c2))
