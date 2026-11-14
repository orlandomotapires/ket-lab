import numpy as np

A = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
B = np.array([[1, 1], [0, 1]])
X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])
K = np.array([[2, 1 - 1j], [1 + 1j, 3]])
psi = np.array([0.6, 0.8j])

Y = np.array([[0, -1j], [1j, 0]])
a_unitary = np.allclose(A.conj().T @ A, np.eye(2))
b_unitary = np.allclose(B.conj().T @ B, np.eye(2))
eigvals, eigvecs = np.linalg.eigh(X)
k_hermitian = np.allclose(K, K.conj().T)
expect_z = np.vdot(psi, Z @ psi)
expect_y = np.vdot(psi, Y @ psi)
