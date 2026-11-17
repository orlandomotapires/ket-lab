import numpy as np
import pennylane as qml

# Ansatz: `layers` layers, each with an R_Y(θ) on every qubit followed by a chain of CZ gates
# between neighbours (0-1, 1-2, ...). Cost: the expectation of Z⊗Z⊗...⊗Z on all qubits.
# Estimate Var[∂C/∂θ] for the very first angle (layer 0, qubit 0) over random angles in [0, 2π).
rng = np.random.default_rng(3)


def gradient_variance(n, layers, samples):
    dev = qml.device("default.qubit", wires=n)

    @qml.qnode(dev)
    def circuit(theta):
        # Build the layers here and return the expectation of Z on every qubit.
        return qml.expval(qml.PauliZ(0))

    # For each sample: draw theta (shape layers × n), get the first-angle gradient with the
    # parameter-shift rule, and collect it. Return the variance of the collected gradients.
    return 0.0


qubits = [2, 3, 4, 5, 6]
# Use layers = n and 100 samples for each number of qubits.
variances = []
