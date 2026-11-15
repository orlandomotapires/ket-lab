import pennylane as qml
from pennylane import numpy as np

# Already defined: hamiltonian(d), the H₂ Hamiltonian (4 qubits, energies in Ha) for a bond
# length d in angstrom, and hf_state = [1, 1, 0, 0].
dev = qml.device("default.qubit", wires=4)

# The ansatz of lesson 3.2 at one bond length, as a starting point. The panel
# draws this circuit; inside your loop, redefine it for each distance.
H = hamiltonian(0.74)


@qml.qnode(dev)
def circuit(theta):
    qml.BasisState(hf_state, wires=[0, 1, 2, 3])
    qml.DoubleExcitation(theta, wires=[0, 1, 2, 3])
    return qml.expval(H)


theta = np.array(0.0, requires_grad=True)

distances = []  # at least 5 bond lengths between 0.5 and 2.0, at least 3 of them in 0.5 to 1.0
steps = 40  # optimizer steps per bond length: the budget is 40

thetas = []  # the optimized angle at each distance
histories = []  # histories[k]: the energy before training and after each step at distances[k]

# For each distance: build H, define the QNode circuit(theta) (Hartree–Fock state,
# DoubleExcitation, expval(H)), train theta from 0.0 and store theta and the energy history.

energies = []  # energies[k]: the final energy at distances[k]
r_eq = None  # the equilibrium bond length, estimated from your curve
