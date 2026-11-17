import numpy as np

# Given data
zero = np.array([1, 0])
one = np.array([0, 1])
plus = np.array([1, 1]) / np.sqrt(2)
I = np.eye(2)
X = np.array([[0, 1], [1, 0]])
s1 = np.array([1, 0, 0, 1]) / np.sqrt(2)
s2 = np.array([1, 1, -1, -1]) / 2

# Replace each placeholder with your computation (Qiskit ordering: qubit 0 is the last factor)
prod = np.zeros(4)        # qubit 1 in |+>, qubit 0 in |0>
op_q0 = np.zeros((4, 4))  # X on qubit 0
op_q1 = np.zeros((4, 4))  # X on qubit 1
after = np.zeros(4)       # op_q0 applied to prod
three = np.zeros(8)       # |+> (x) |+> (x) |+>
s1_product = False        # is s1 a product state?
s2_product = False        # is s2 a product state?
