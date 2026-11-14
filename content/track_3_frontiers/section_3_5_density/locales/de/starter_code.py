import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)


def error_kraus(p_x, p_z):
    # Kraus-Operatoren des Fehlers: nichts, X oder Z, mit den Wahrscheinlichkeiten 1 − p_x − p_z, p_x und p_z.
    return [np.eye(2)]


@qml.qnode(dev)
def circuit(p_x, p_z):
    qml.Hadamard(wires=0)
    qml.T(wires=0)
    # Füge hier den Fehler ein (qml.QubitChannel).
    qml.adjoint(qml.T(wires=0))
    qml.Hadamard(wires=0)
    return qml.density_matrix(wires=0)


p_x = 0.2
p_z = 0.2
rho = circuit(p_x, p_z)

# Berechne p_wrong (Wahrscheinlichkeit, 1 zu messen) und purity (Tr ρ²).
