# Idea: the ansatz of lesson 3.2 stays the same, only the Hamiltonian changes with the bond length.
# Train it from θ = 0 at each distance, then fit a parabola near the minimum for the equilibrium.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=4)

# Dense near the minimum (0.6 to 0.8 Å) for the parabola, sparse at long distance to show the rise.
distances = [0.5, 0.6, 0.7, 0.8, 1.0, 1.5, 2.0]
steps = 40

thetas = []
histories = []

for d in distances:
    # The integrals depend on d, so each distance has its own Hamiltonian and its own optimum θ.
    H = hamiltonian(d)

    @qml.qnode(dev)
    def circuit(theta):
        qml.BasisState(hf_state, wires=[0, 1, 2, 3])
        qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])
        return qml.expval(H)

    # Restart from θ = 0 (Hartree–Fock) every time, so each training uses the same 40-step budget.
    theta = np.array(0.0, requires_grad=True)
    optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
    history = [float(circuit(theta))]
    for _ in range(steps):
        theta = optimizer.step(circuit, theta)
        history.append(float(circuit(theta)))
    # Keep the angle and the full history: the validator rebuilds each energy from the angle.
    thetas.append(float(theta))
    histories.append(history)

# The last history entry is the energy of the final state at that distance.
energies = [history[-1] for history in histories]

# Equilibrium: vertex of the parabola through the three lowest points.
lowest = sorted(range(len(distances)), key=lambda k: energies[k])[:3]
c2, c1, c0 = np.polyfit([distances[k] for k in lowest], [energies[k] for k in lowest], 2)
r_eq = float(-c1 / (2 * c2))
