import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)


def error_kraus(p_x, p_z):
    # Kraus operators of the error: nothing, X or Z, with probabilities 1 − p_x − p_z, p_x and p_z.
    return [np.eye(2)]


@qml.qnode(dev)
def circuit(p_x, p_z):
    qml.Hadamard(wires=0)
    qml.T(wires=0)
    # Insert the error here (qml.QubitChannel).
    qml.adjoint(qml.T(wires=0))
    qml.Hadamard(wires=0)
    return qml.density_matrix(wires=0)


p_x = 0.2
p_z = 0.2
rho = circuit(p_x, p_z)

# Compute p_wrong (probability of measuring 1) and purity (Tr ρ²).
