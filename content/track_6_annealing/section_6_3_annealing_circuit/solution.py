from qiskit import QuantumCircuit

# Idea: cut the anneal H(s) = (1 - s) H_B + s H_P into p Trotter steps. In step k the
# schedule is frozen at s = (k - 1/2) / p, and the step applies the cost layer
# e^{-i s H_P dt} followed by the mixer layer e^{-i (1 - s) H_B dt}. A long total time T
# is needed because the energy gap of this instance gets small near the end.
h = [1 / 3, 2 / 3, 1]
J = {(0, 1): 1 / 6, (0, 2): 1 / 4, (1, 2): 1 / 2}

# The gap is small, so T must be large for the state to follow the ground state.
# The step dt = T / p stays near 1 so that the Trotter error is small.
T = 120
p = 100
dt = T / p

qc = QuantumCircuit(3)
# Start in |+++>, the ground state of H_B = -(X0 + X1 + X2).
qc.h([0, 1, 2])

for k in range(1, p + 1):
    # The midpoint of the step is used as the value of s for the whole step.
    s = (k - 0.5) / p

    # rz(θ) = e^{-iθZ/2}, so e^{-i s h_i dt Z} needs the angle 2 s h_i dt.
    for i in range(3):
        qc.rz(2 * s * h[i] * dt, i)
    # The same factor 2 for rzz(θ) = e^{-iθ ZZ/2}.
    for (i, j), coupling in J.items():
        qc.rzz(2 * s * coupling * dt, i, j)

    # e^{-i (1 - s) dt H_B} = e^{+i (1 - s) dt X}, and rx(θ) = e^{-iθX/2}, so the angle is negative.
    for i in range(3):
        qc.rx(-2 * (1 - s) * dt, i)
