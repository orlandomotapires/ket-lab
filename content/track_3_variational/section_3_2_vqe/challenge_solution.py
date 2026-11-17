# Idea: from Hartree–Fock a single excitation only moves one electron to a neighbouring orbital, and
# H has no matrix element between that state and Hartree–Fock, so the energy has zero slope at θ = 0
# and every pair ends at the Hartree–Fock energy. The gap to the exact value is the correlation energy.
import pennylane as qml
from pennylane import numpy as np
from itertools import combinations

dev = qml.device("default.qubit", wires=4)
EXACT = -1.1372838


def energy_fn(i, j):
    # One circuit per pair of wires: Hartree–Fock, then a single excitation between wires i and j.
    @qml.qnode(dev)
    def circuit(theta):
        qml.BasisState(hf_state, wires=[0, 1, 2, 3])
        qml.SingleExcitation(theta, wires=[i, j])
        return qml.expval(H)

    return circuit


best_energy = {}
for i, j in combinations(range(4), 2):
    circuit = energy_fn(i, j)
    # Start away from 0: at θ = 0 the slope is exactly zero, so the optimizer would not even move.
    theta = np.array(0.5, requires_grad=True)
    optimizer = qml.GradientDescentOptimizer(stepsize=0.4)
    for step in range(40):
        theta = optimizer.step(circuit, theta)
    # The lowest energy this one gate can reach on the Hartree–Fock state.
    best_energy[(i, j)] = float(circuit(theta))

# 1 Ha = 1000 mHa; the best of the six is still above the exact ground state.
gap_mha = (min(best_energy.values()) - EXACT) * 1000
print(best_energy, gap_mha)
