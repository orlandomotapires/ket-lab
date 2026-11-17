from qiskit import QuantumCircuit

# Three-qubit instance of lessons 6.1 and 6.2: E(s) = sum_i h[i] s_i + sum_{i<j} J[i, j] s_i s_j
h = [1 / 3, 2 / 3, 1]
J = {(0, 1): 1 / 6, (0, 2): 1 / 4, (1, 2): 1 / 2}

T = 10  # total annealing time
p = 10  # number of Trotter steps
dt = T / p

qc = QuantumCircuit(3)
qc.h([0, 1, 2])  # the ground state of H_B = -(X0 + X1 + X2)

# For k = 1..p: s = (k - 0.5) / p, then the cost layer (rz and rzz) and the mixer layer (rx).
# Remember that rz(θ) = e^{-iθZ/2}, rzz(θ) = e^{-iθZZ/2} and the mixer has a minus sign.
