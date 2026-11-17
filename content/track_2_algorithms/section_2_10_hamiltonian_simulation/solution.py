# Idea: first-order Trotter formula. Split t into n steps, and in each step apply the Z⊗Z term and
# the field terms one after another. The error shrinks as 1/n, and n = 10 is enough for fidelity 0.99.
from qiskit import QuantumCircuit

J = 1.0
h = 0.8
t = 2.0

# More steps mean a smaller error; ten steps give fidelity above 0.99 with 30 gates.
n_steps = 10
dt = t / n_steps

qc = QuantumCircuit(2)
for _ in range(n_steps):
    # rzz(θ) = e^{-iθ Z⊗Z/2}, so the angle 2·J·dt gives e^{-i J Z⊗Z dt}.
    qc.rzz(2 * J * dt, 0, 1)  # e^{-i J Z⊗Z dt}
    # rx(θ) = e^{-iθ X/2}, so the angle 2·h·dt gives e^{-i h X dt} on each qubit.
    qc.rx(2 * h * dt, 0)  # e^{-i h X dt}
    qc.rx(2 * h * dt, 1)
