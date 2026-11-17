# Idea: a generic layered circuit that knows no chemistry can still reach the ground state if it has enough rotations and entanglers.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=4)
LAYERS = 3


@qml.qnode(dev)
def circuit(theta):
    # Hartree–Fock reference: a good starting point that already holds the right number of electrons.
    qml.BasisState(hf_state, wires=[0, 1, 2, 3])
    k = 0
    for _ in range(LAYERS):
        # A rotation on every qubit gives each one its own tunable direction.
        for q in range(4):
            qml.RY(theta[k], wires=q)
            k += 1
        # A ladder of CNOTs spreads the entanglement along the chain.
        for q in range(3):
            qml.CNOT(wires=[q, q + 1])
    # A last rotation layer so the final CNOTs are not the end of the circuit.
    for q in range(4):
        qml.RY(theta[k], wires=q)
        k += 1
    return qml.expval(H)


# Small random angles keep the start close to Hartree–Fock but break its symmetry.
np.random.seed(0)
theta = np.array(np.random.uniform(-0.3, 0.3, 4 * (LAYERS + 1)), requires_grad=True)
energies = [float(circuit(theta))]

# Adam adapts the step of each angle, which suits a 16-angle landscape better than plain descent.
optimizer = qml.AdamOptimizer(0.1)
for step in range(150):
    theta = optimizer.step(circuit, theta)
    energies.append(float(circuit(theta)))
