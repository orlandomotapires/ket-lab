# Idea: the symmetric (second-order) step has error O(dt³) instead of O(dt²), so fewer steps suffice.
# Merging the neighboring half steps of the field keeps the gate count close to the first-order one.
from qiskit import QuantumCircuit

J = 1.0
h = 0.8
t = 2.0

n_steps = 5
dt = t / n_steps

# Second-order step: half step of the field, full Z⊗Z step, half step of the field.
# The half steps of consecutive steps are merged into one full rx.
qc = QuantumCircuit(2)
# Opening half step of the field: e^{-i h X dt/2} on each qubit.
qc.rx(h * dt, 0)
qc.rx(h * dt, 1)
for step in range(n_steps):
    qc.rzz(2 * J * dt, 0, 1)
    # Closing half step plus the next opening half step make one full rx; the last step keeps only the half.
    angle = h * dt if step == n_steps - 1 else 2 * h * dt
    qc.rx(angle, 0)
    qc.rx(angle, 1)
