# Idea: unitarity and hermiticity are statements about the conjugate transpose, tested with
# np.allclose because floating-point products are not exact. Expectation values are ⟨ψ|A|ψ⟩.
import numpy as np

A = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
B = np.array([[1, 1], [0, 1]])
X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])
K = np.array([[2, 1 - 1j], [1 + 1j, 3]])
psi = np.array([0.6, 0.8j])

# Pauli Y: the entries -i and i make it complex, yet Y† = Y.
Y = np.array([[0, -1j], [1j, 0]])
# U is unitary when U†U = I; A is the Hadamard matrix, so this is True.
a_unitary = np.allclose(A.conj().T @ A, np.eye(2))
# B† B = [[1, 1], [1, 2]] is not the identity, so B changes norms and is not a gate.
b_unitary = np.allclose(B.conj().T @ B, np.eye(2))
# X is Hermitian: eigh returns the real eigenvalues (−1, 1) and orthonormal eigenvectors as columns.
eigvals, eigvecs = np.linalg.eigh(X)
# Hermitian means K = K†: real diagonal and conjugate off-diagonal entries.
k_hermitian = np.allclose(K, K.conj().T)
# ⟨Z⟩ = |α|² − |β|² = 0.36 − 0.64, the probability of +1 minus that of −1.
expect_z = np.vdot(psi, Z @ psi)
# vdot conjugates ψ for the bra; the result is real because Y is Hermitian.
expect_y = np.vdot(psi, Y @ psi)
