# Idea: start from the Hartree–Fock state and let one double excitation mix it with |0011⟩, the only
# other state the H₂ ground state needs. Minimizing ⟨H⟩ over that one angle gives the exact energy.
import pennylane as qml
from pennylane import numpy as np

dev = qml.device("default.qubit", wires=4)


@qml.qnode(dev)
def circuit(theta):
    # Hartree–Fock reference |1100⟩: the two electrons in the two lowest spin orbitals.
    qml.BasisState(hf_state, wires=[0, 1, 2, 3])
    # Rotates between |1100⟩ and |0011⟩, which adds the electron correlation Hartree–Fock lacks.
    qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])
    # The energy ⟨ψ(θ)|H|ψ(θ)⟩ is the cost; by the variational principle it never drops below E₀.
    return qml.expval(H)


# θ = 0 is exactly the Hartree–Fock state, so the first energy is the Hartree–Fock energy.
theta = np.array(0.0, requires_grad=True)
optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
energies = [float(circuit(theta))]

for step in range(40):
    # One gradient step lowers the energy; the loop approaches E₀ from above.
    theta = optimizer.step(circuit, theta)
    energies.append(float(circuit(theta)))

energy = energies[-1]
