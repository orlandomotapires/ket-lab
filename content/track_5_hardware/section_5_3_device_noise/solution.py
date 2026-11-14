import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)

T1 = 100.0
T2 = 80.0
t_wait = 50.0


@qml.qnode(dev)
def idle(T1, T2, t_wait):
    qml.Hadamard(wires=0)
    gamma = 1 - np.exp(-t_wait / T1)  # probability of decaying to |0⟩ during t_wait
    rate_phi = 1 / T2 - 1 / (2 * T1)  # pure dephasing rate, 1/T_phi
    lam = 1 - np.exp(-2 * t_wait * rate_phi)
    qml.AmplitudeDamping(gamma, wires=0)
    qml.PhaseDamping(lam, wires=0)
    return qml.density_matrix(wires=0)


rho = idle(T1, T2, t_wait)
p1 = np.real(rho[1, 1])
coherence = np.abs(rho[0, 1])
