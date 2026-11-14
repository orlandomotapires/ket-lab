import pennylane as qml
from pennylane import numpy as np

# Já disponíveis: H (o Hamiltoniano do H₂, 4 qubits) e hf_state = [1, 1, 0, 0].
dev = qml.device("default.qubit", wires=4)


@qml.qnode(dev)
def circuit(theta):
    # 1. Estado de Hartree-Fock com qml.BasisState.
    # 2. Excitação dupla com o ângulo theta.
    return qml.expval(H)


theta = np.array(0.0, requires_grad=True)
energies = [float(circuit(theta))]

# 3. Otimize theta com qml.GradientDescentOptimizer e guarde cada energia em energies.
