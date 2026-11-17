# Idea: relaxation and dephasing are two channels applied in sequence. Amplitude damping fixes the
# population decay e^{-t/T1}; phase damping supplies the extra coherence loss that T2 requires.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.mixed", wires=1)

T1 = 100.0
T2 = 80.0
t_wait = 50.0


@qml.qnode(dev)
def idle(T1, T2, t_wait):
    # |+⟩ has the largest coherence ρ01 = 1/2, so both decays are visible.
    qml.Hadamard(wires=0)
    # γ = 1 − e^{-t/T1} is the probability of decaying to |0⟩, so ρ11 shrinks by e^{-t/T1}.
    gamma = 1 - np.exp(-t_wait / T1)  # probability of decaying to |0⟩ during t_wait
    # Amplitude damping already scales ρ01 by e^{-t/(2 T1)}; the rest of 1/T2 is pure dephasing, 1/T_φ.
    rate_phi = 1 / T2 - 1 / (2 * T1)  # pure dephasing rate, 1/T_phi
    # Phase damping multiplies ρ01 by √(1 − λ), so λ = 1 − e^{-2t/T_φ} gives the missing factor e^{-t/T_φ}.
    lam = 1 - np.exp(-2 * t_wait * rate_phi)
    qml.AmplitudeDamping(gamma, wires=0)
    qml.PhaseDamping(lam, wires=0)
    return qml.density_matrix(wires=0)


rho = idle(T1, T2, t_wait)
# The population of |1⟩ is ρ11 and the coherence is the size of the off-diagonal element ρ01.
p1 = np.real(rho[1, 1])
coherence = np.abs(rho[0, 1])
