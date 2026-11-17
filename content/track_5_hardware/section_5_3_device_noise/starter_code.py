import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)

T1 = 100.0  # µs: energy relaxation time
T2 = 80.0  # µs: coherence time (never larger than 2 T1)
t_wait = 50.0  # µs: the qubit idles for this long


@qml.qnode(dev)
def idle(T1, T2, t_wait):
    qml.Hadamard(wires=0)  # prepare |+⟩
    # Idle noise goes here: amplitude damping with gamma, then phase damping with lam.
    return qml.density_matrix(wires=0)


rho = idle(T1, T2, t_wait)

# From rho: the probability of measuring 1 and the size of the coherence |ρ01|.
p1 = 0.0
coherence = 0.0
