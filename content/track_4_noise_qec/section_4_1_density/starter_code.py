import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)


def error_kraus(p_x, p_z):
    # Kraus operators: sqrt(1 − p_x − p_z)·I, sqrt(p_x)·X and sqrt(p_z)·Z.
    return [np.eye(2)]


@qml.qnode(dev)
def circuit(p_x, p_z):
    qml.Hadamard(wires=0)
    qml.T(wires=0)
    # Apply the error here with qml.QubitChannel.
    qml.adjoint(qml.T(wires=0))
    qml.Hadamard(wires=0)
    return qml.density_matrix(wires=0)


p_x = 0.2
p_z = 0.2
rho = circuit(p_x, p_z)

# Compute p_wrong (the probability of measuring 1) and purity (Tr ρ²) from rho.
