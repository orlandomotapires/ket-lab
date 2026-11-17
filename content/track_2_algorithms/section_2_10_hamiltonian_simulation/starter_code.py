from qiskit import QuantumCircuit

J = 1.0  # coupling in J Z⊗Z
h = 0.8  # field in h (X⊗I + I⊗X)
t = 2.0  # evolution time

n_steps = 1  # number of Trotter steps
dt = t / n_steps

qc = QuantumCircuit(2)  # starts in |00⟩

# One Trotter step is e^{-iJ Z⊗Z dt} followed by e^{-ih X dt} on each qubit.
# Repeat it n_steps times.
