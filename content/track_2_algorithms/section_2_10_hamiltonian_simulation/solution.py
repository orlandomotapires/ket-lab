from qiskit import QuantumCircuit

J = 1.0
h = 0.8
t = 2.0

n_steps = 10
dt = t / n_steps

qc = QuantumCircuit(2)
for _ in range(n_steps):
    qc.rzz(2 * J * dt, 0, 1)  # e^{-i J Z⊗Z dt}
    qc.rx(2 * h * dt, 0)  # e^{-i h X dt}
    qc.rx(2 * h * dt, 1)
