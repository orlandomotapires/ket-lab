import pennylane as qml
from pennylane import numpy as np

# Already defined: H (the H₂ Hamiltonian on 4 qubits) and hf_state = [1, 1, 0, 0].
dev = qml.device("default.qubit", wires=4)


@qml.qnode(dev)
def circuit(theta):
    # 1. Prepare the Hartree–Fock state with qml.BasisState.
    # 2. Apply a double excitation with angle theta.
    return qml.expval(H)


theta = np.array(0.0, requires_grad=True)
energies = [float(circuit(theta))]

# 3. Minimize the energy over theta with qml.GradientDescentOptimizer and append each energy to energies.
