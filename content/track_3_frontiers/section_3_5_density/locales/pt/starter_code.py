import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)


def error_kraus(p_x, p_z):
    # Operadores de Kraus do erro: nada, X ou Z, com probabilidades 1 − p_x − p_z, p_x e p_z.
    return [np.eye(2)]


@qml.qnode(dev)
def circuit(p_x, p_z):
    qml.Hadamard(wires=0)
    qml.T(wires=0)
    # Insira aqui o erro (qml.QubitChannel).
    qml.adjoint(qml.T(wires=0))
    qml.Hadamard(wires=0)
    return qml.density_matrix(wires=0)


p_x = 0.2
p_z = 0.2
rho = circuit(p_x, p_z)

# Calcule p_wrong (probabilidade de medir 1) e purity (Tr ρ²).
