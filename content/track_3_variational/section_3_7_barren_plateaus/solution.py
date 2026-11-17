# Idea: the parameter-shift rule gives ∂C/∂θ exactly from two circuit runs; repeating it on random angles estimates its variance.
import numpy as np
import pennylane as qml

rng = np.random.default_rng(3)


def gradient_variance(n, layers, samples):
    dev = qml.device("default.qubit", wires=n)

    @qml.qnode(dev)
    def circuit(theta):
        for layer in range(layers):
            # One R_Y on every qubit, then a chain of CZ gates between neighbours.
            for q in range(n):
                qml.RY(theta[layer][q], wires=q)
            for q in range(n - 1):
                qml.CZ(wires=[q, q + 1])
        # A global cost: Z on every qubit at once.
        return qml.expval(qml.prod(*[qml.PauliZ(q) for q in range(n)]))

    gradients = []
    for _ in range(samples):
        # Random angles in [0, 2π) are the typical starting point of a training run.
        theta = rng.uniform(0, 2 * np.pi, (layers, n))
        plus, minus = theta.copy(), theta.copy()
        plus[0][0] += np.pi / 2
        minus[0][0] -= np.pi / 2
        # Parameter-shift rule for the first angle.
        gradients.append((float(circuit(plus)) - float(circuit(minus))) / 2)
    return float(np.var(gradients))


qubits = [2, 3, 4, 5, 6]
# The depth grows with the width: layers = n.
variances = [gradient_variance(n, n, 100) for n in qubits]
