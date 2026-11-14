import pennylane as qml
from pennylane import numpy as np

# Bereits verfügbar: H (der Hamilton-Operator von H₂, 4 Qubits) und hf_state = [1, 1, 0, 0].
dev = qml.device("default.qubit", wires=4)


@qml.qnode(dev)
def circuit(theta):
    # 1. Hartree-Fock-Zustand mit qml.BasisState.
    # 2. Doppelanregung mit dem Winkel theta.
    return qml.expval(H)


theta = np.array(0.0, requires_grad=True)
energies = [float(circuit(theta))]

# 3. Optimiere theta mit qml.GradientDescentOptimizer und speichere jede Energie in energies.
