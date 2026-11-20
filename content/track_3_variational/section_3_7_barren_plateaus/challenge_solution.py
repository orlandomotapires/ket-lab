# Idea: the global cost Z⊗…⊗Z needs every qubit to carry information, and that is what makes its
# gradient vanish. A cost on qubit 0 alone is only reached by the few gates near that qubit, so with
# two layers its gradient variance does not depend on how many qubits the circuit has.
import numpy as np
import pennylane as qml

rng = np.random.default_rng(3)


def gradient_variance(n, layers, samples, local=False):
    dev = qml.device("default.qubit", wires=n)

    @qml.qnode(dev)
    def circuit(theta):
        for layer in range(layers):
            for q in range(n):
                qml.RY(theta[layer][q], wires=q)
            for q in range(n - 1):
                qml.CZ(wires=[q, q + 1])
        if local:
            # The only change from the mission: the cost is Z on qubit 0 alone.
            return qml.expval(qml.PauliZ(0))
        return qml.expval(qml.prod(*[qml.PauliZ(q) for q in range(n)]))

    gradients = []
    for _ in range(samples):
        theta = rng.uniform(0, 2 * np.pi, (layers, n))
        plus, minus = theta.copy(), theta.copy()
        plus[0][0] += np.pi / 2
        minus[0][0] -= np.pi / 2
        gradients.append((float(circuit(plus)) - float(circuit(minus))) / 2)
    return float(np.var(gradients))


def local_variance(n, layers, samples):
    return gradient_variance(n, layers, samples, local=True)


n_values = [2, 4, 6, 8, 10]
# Two layers for both costs, so that the only difference between the two lists is the cost.
local_vars = [local_variance(n, 2, 100) for n in n_values]
global_vars = [gradient_variance(n, 2, 100) for n in n_values]
print(local_vars)
print(global_vars)
