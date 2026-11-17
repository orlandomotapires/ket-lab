# Idea: with every angle at zero the circuit is just the three CNOT ladders on |1100⟩, which give the
# basis state |1010⟩. That state is an eigenstate of H, so the gradient is exactly zero and the
# optimizer has nowhere to go. A few small random angles break the tie and training works as before.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=4)
LAYERS = 3


@qml.qnode(dev)
def circuit(theta):
    # Hartree–Fock reference, as in the mission.
    qml.BasisState(hf_state, wires=[0, 1, 2, 3])
    k = 0
    for _ in range(LAYERS):
        for q in range(4):
            qml.RY(theta[k], wires=q)
            k += 1
        for q in range(3):
            qml.CNOT(wires=[q, q + 1])
    for q in range(4):
        qml.RY(theta[k], wires=q)
        k += 1
    return qml.expval(H)


# The bad start: all sixteen angles at zero.
theta_zero = np.zeros(4 * (LAYERS + 1), requires_grad=True)
energy_zero = float(circuit(theta_zero))
# The gradient norm at that start: exactly zero, because the state is an eigenstate of H.
grad_norm_zero = float(np.linalg.norm(qml.grad(circuit)(theta_zero)))

# A short Adam run from zero: the energy does not change because every step uses a zero gradient.
optimizer = qml.AdamOptimizer(0.1)
energies_zero = [energy_zero]
for step in range(20):
    theta_zero = optimizer.step(circuit, theta_zero)
    energies_zero.append(float(circuit(theta_zero)))

# The fix: small random angles, as in the mission, and the same Adam training.
np.random.seed(0)
theta = np.array(np.random.uniform(-0.3, 0.3, 4 * (LAYERS + 1)), requires_grad=True)
energies = [float(circuit(theta))]
optimizer = qml.AdamOptimizer(0.1)
for step in range(150):
    theta = optimizer.step(circuit, theta)
    energies.append(float(circuit(theta)))
