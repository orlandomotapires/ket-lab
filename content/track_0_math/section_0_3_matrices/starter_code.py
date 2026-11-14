import numpy as np

# Given data
A = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
B = np.array([[1, 1], [0, 1]])
X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])
K = np.array([[2, 1 - 1j], [1 + 1j, 3]])
psi = np.array([0.6, 0.8j])

# Replace each placeholder with your computation
Y = np.zeros((2, 2))        # Pauli Y matrix
a_unitary = False           # is A unitary? (True or False)
b_unitary = False           # is B unitary?
eigvals = np.zeros(2)       # eigenvalues of X
eigvecs = np.zeros((2, 2))  # eigenvectors of X, as columns
k_hermitian = False         # is K Hermitian?
expect_z = 0                # <psi|Z|psi>
expect_y = 0                # <psi|Y|psi>
