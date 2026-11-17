# Idea: write the error as Kraus operators, put it between T and T† with a channel, and read
# the wrong-answer probability and the purity off the final density matrix.
import pennylane as qml
from pennylane import numpy as np

# default.mixed keeps the density matrix, which is needed to represent a random error.
dev = qml.device("default.mixed", wires=1)


def error_kraus(p_x, p_z):
    identity = np.eye(2)
    pauli_x = np.array([[0, 1], [1, 0]])
    pauli_z = np.array([[1, 0], [0, -1]])
    # Weights √p on each Pauli make the probabilities add up to 1, so that ΣK†K = I.
    return [np.sqrt(1 - p_x - p_z) * identity, np.sqrt(p_x) * pauli_x, np.sqrt(p_z) * pauli_z]


@qml.qnode(dev)
def circuit(p_x, p_z):
    # H T T† H is the identity, so the ideal output is |0⟩.
    qml.Hadamard(wires=0)
    qml.T(wires=0)
    # The channel acts on ρ, not on a state vector: with probability p_x or p_z it applies X or Z.
    qml.QubitChannel(error_kraus(p_x, p_z), wires=0)
    qml.adjoint(qml.T(wires=0))
    qml.Hadamard(wires=0)
    # Return ρ itself: a mixed state has no state vector.
    return qml.density_matrix(wires=0)


p_x = 0.2
p_z = 0.2
rho = circuit(p_x, p_z)
# The ideal output is |0⟩, so ρ[1, 1] is the probability that the result is wrong.
p_wrong = np.real(rho[1, 1])
# Tr(ρ²) is below 1 because the random error left a mixed state.
purity = np.real(np.trace(rho @ rho))
