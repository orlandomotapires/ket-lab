# Idea: amplitude damping has two Kraus operators, "nothing happens" (with the |1> amplitude
# weakened) and "the qubit decays" (|1> becomes |0>). Unlike a Pauli error it pushes the Bloch
# vector toward |0>, so even the maximally mixed state ends up away from the centre.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)


def damping_kraus(gamma):
    # K0 keeps |0> and shrinks the amplitude of |1> by sqrt(1 - gamma): the no-decay branch.
    k0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]])
    # K1 takes |1> to |0> with amplitude sqrt(gamma): the decay branch.
    k1 = np.array([[0, np.sqrt(gamma)], [0, 0]])
    # K0†K0 + K1†K1 = diag(1, 1 - gamma) + diag(0, gamma) = I, so the trace is preserved.
    return [k0, k1]


@qml.qnode(dev)
def damped(gamma):
    # H prepares |+>, the state with the most to lose: it is a superposition and has weight on |1>.
    qml.Hadamard(wires=0)
    qml.QubitChannel(damping_kraus(gamma), wires=0)
    return qml.density_matrix(wires=0)


def apply_channel(rho, gamma):
    # The channel acts on any density matrix as the sum of K rho K†.
    return sum(k @ rho @ k.conj().T for k in damping_kraus(gamma))


def bloch_vector(rho):
    # The components are the expectation values of X, Y and Z: Tr(rho P).
    x = np.real(rho[0, 1] + rho[1, 0])
    y = np.real(1j * (rho[0, 1] - rho[1, 0]))
    z = np.real(rho[0, 0] - rho[1, 1])
    return [float(x), float(y), float(z)]


gamma = 0.36
rho_plus = damped(gamma)
bloch_plus = bloch_vector(rho_plus)
purity_plus = float(np.real(np.trace(rho_plus @ rho_plus)))
# A Pauli mixture leaves I/2 where it is. Here the z component of the output is not zero.
z_from_mixed = bloch_vector(apply_channel(np.eye(2) / 2, gamma))[2]
