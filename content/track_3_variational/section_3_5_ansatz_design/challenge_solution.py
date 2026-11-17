# Idea: one R_Y(π/2) on qubit 0 makes (|0⟩ + |1⟩)/√2, and a CNOT copies that choice onto qubit 1,
# which gives |Φ⁺⟩. One angle is enough; the other three of the mission were redundant.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=2)


@qml.qnode(dev)
def circuit(params):
    # A single rotation: cos(θ/2)|0⟩ + sin(θ/2)|1⟩ on qubit 0, equal weights at θ = π/2.
    qml.RY(params[0], wires=0)
    # The CNOT sends |00⟩ to |00⟩ and |10⟩ to |11⟩, so the two qubits agree: cos(θ/2)|00⟩ + sin(θ/2)|11⟩.
    qml.CNOT(wires=[0, 1])
    return qml.expval(H)


# One angle, one entry. The fidelity is (1 + sin θ)/2, so the slope at the start is not zero.
params = np.array([0.4], requires_grad=True)
optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
energies = [float(circuit(params))]

# Gradient descent on −F climbs to θ = π/2, where the fidelity is 1.
for step in range(60):
    params = optimizer.step(circuit, params)
    energies.append(float(circuit(params)))
