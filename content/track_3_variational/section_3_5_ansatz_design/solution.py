# Idea: the CNOT turns a product state into an entangled one, and a second layer of
# R_Y rotations lets the optimizer tune the amplitudes. Four angles are enough.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=2)


@qml.qnode(dev)
def circuit(params):
    # First rotation layer: puts each qubit on the x-z plane of its Bloch sphere.
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    # Entangling gate: a product state cannot have fidelity above 1/2 with |Φ⁺⟩.
    qml.CNOT(wires=[0, 1])
    # Second rotation layer: refines the amplitudes after the entangling step.
    qml.RY(params[2], wires=0)
    qml.RY(params[3], wires=1)
    return qml.expval(H)


# One starting angle per rotation, away from the symmetric point.
params = np.array([0.4, 1.2, 0.3, 0.8], requires_grad=True)
optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
energies = [float(circuit(params))]

# Gradient descent on the cost -F: each step raises the fidelity with |Φ⁺⟩.
for step in range(60):
    params = optimizer.step(circuit, params)
    energies.append(float(circuit(params)))
