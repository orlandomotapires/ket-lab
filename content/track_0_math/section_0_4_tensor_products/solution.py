import numpy as np

zero = np.array([1, 0])
one = np.array([0, 1])
plus = np.array([1, 1]) / np.sqrt(2)
I = np.eye(2)
X = np.array([[0, 1], [1, 0]])
s1 = np.array([1, 0, 0, 1]) / np.sqrt(2)
s2 = np.array([1, 1, -1, -1]) / 2

prod = np.kron(plus, zero)
op_q0 = np.kron(I, X)
op_q1 = np.kron(X, I)
after = op_q0 @ prod
three = np.kron(np.kron(plus, plus), plus)
s1_product = bool(np.isclose(s1[0] * s1[3], s1[1] * s1[2]))
s2_product = bool(np.isclose(s2[0] * s2[3], s2[1] * s2[2]))
