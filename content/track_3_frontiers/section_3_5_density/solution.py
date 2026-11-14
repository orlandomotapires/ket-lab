import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)


def error_kraus(p_x, p_z):
    identity = np.eye(2)
    pauli_x = np.array([[0, 1], [1, 0]])
    pauli_z = np.array([[1, 0], [0, -1]])
    return [np.sqrt(1 - p_x - p_z) * identity, np.sqrt(p_x) * pauli_x, np.sqrt(p_z) * pauli_z]


@qml.qnode(dev)
def circuit(p_x, p_z):
    qml.Hadamard(wires=0)
    qml.T(wires=0)
    qml.QubitChannel(error_kraus(p_x, p_z), wires=0)
    qml.adjoint(qml.T(wires=0))
    qml.Hadamard(wires=0)
    return qml.density_matrix(wires=0)


p_x = 0.2
p_z = 0.2
rho = circuit(p_x, p_z)
p_wrong = np.real(rho[1, 1])
purity = np.real(np.trace(rho @ rho))
