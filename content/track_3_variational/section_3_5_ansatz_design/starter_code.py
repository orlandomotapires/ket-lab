import pennylane as qml
from pennylane import numpy as np

# Already defined: H = -|Φ⁺⟩⟨Φ⁺|, so the cost is -1 times the fidelity with the Bell state.
dev = qml.device("default.qubit", wires=2)


@qml.qnode(dev)
def circuit(params):
    # This product ansatz cannot reach |Φ⁺⟩. Add an entangling gate and more
    # rotations (at most 4 rotation angles in total), one entry of params each.
    qml.RY(params[0], wires=0)
    qml.RY(params[1], wires=1)
    return qml.expval(H)


# One starting angle per rotation: change the length when you add rotations.
params = np.array([0.4, 1.2], requires_grad=True)
optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
energies = [float(circuit(params))]

for step in range(60):
    params = optimizer.step(circuit, params)
    energies.append(float(circuit(params)))
