import pennylane as qml
from pennylane import numpy as np

# Already defined: H (the H₂ Hamiltonian on 4 qubits) and hf_state = [1, 1, 0, 0].
dev = qml.device("default.qubit", wires=4)
LAYERS = 3


@qml.qnode(dev)
def circuit(theta):
    # 1. Prepare the Hartree–Fock state with qml.BasisState.
    # 2. Repeat LAYERS times: R_Y on every qubit, then CNOT between neighbours (0-1, 1-2, 2-3).
    # 3. Finish with one more layer of R_Y. In total theta needs 4 * (LAYERS + 1) = 16 entries.
    return qml.expval(H)


np.random.seed(0)
theta = np.array(np.random.uniform(-0.3, 0.3, 4 * (LAYERS + 1)), requires_grad=True)
energies = [float(circuit(theta))]

# 4. Minimize the energy with qml.AdamOptimizer(0.1) for 150 steps and append each energy to energies.
