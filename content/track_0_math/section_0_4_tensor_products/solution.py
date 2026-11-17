# Idea: np.kron builds multi-qubit vectors and operators. Qiskit's ordering puts the highest qubit
# first and qubit 0 last, and the product-state test compares a00·a11 with a01·a10.
import numpy as np

zero = np.array([1, 0])
one = np.array([0, 1])
plus = np.array([1, 1]) / np.sqrt(2)
I = np.eye(2)
X = np.array([[0, 1], [1, 0]])
s1 = np.array([1, 0, 0, 1]) / np.sqrt(2)
s2 = np.array([1, 1, -1, -1]) / 2

# Qubit 1 is the first factor and qubit 0 the last, so |+⟩ on qubit 1 and |0⟩ on qubit 0 is kron(plus, zero).
prod = np.kron(plus, zero)
# X on qubit 0 acts on the last factor, with the identity on qubit 1: I ⊗ X.
op_q0 = np.kron(I, X)
# X on qubit 1 acts on the first factor: X ⊗ I.
op_q1 = np.kron(X, I)
# (I ⊗ X)(|+⟩ ⊗ |0⟩) = |+⟩ ⊗ X|0⟩ = |+⟩ ⊗ |1⟩: only the factor of qubit 0 changes.
after = op_q0 @ prod
# Three qubits need two nested Kronecker products, giving 2³ = 8 entries.
three = np.kron(np.kron(plus, plus), plus)
# A product state has a00·a11 = a01·a10. For s1 this is 1/2 against 0, so s1 is entangled.
s1_product = bool(np.isclose(s1[0] * s1[3], s1[1] * s1[2]))
# For s2 both sides equal −1/4, so s2 = |−⟩ ⊗ |+⟩ is a product state.
s2_product = bool(np.isclose(s2[0] * s2[3], s2[1] * s2[2]))
