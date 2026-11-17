import itertools
import numpy as np

# Four jobs, indexed 0 to 3, with these values. Exactly two must run.
v = [5, 4, 3, 2]
# Pairs of jobs that cannot both run.
conflicts = [(0, 1), (1, 2)]
B = 6  # penalty for running both jobs of a conflicting pair
A_used = 4  # penalty weight of the count constraint, used from the Q step on
A_big = 20  # an oversized weight, for the last comparison
penalties = [0.5, 1, 1.5, 2, 2.5, 3, 4, 6]  # candidate weights for A_min
T_values = [5, 20, 80]  # total annealing times

# Penalized cost of x in {0,1}^4:
#   -sum(v_i x_i) + A (sum(x_i) - 2)^2 + B sum_{conflicts} x_i x_j
# Convention of the track: spin s = 1 - 2x, qubit i carries job i, Qiskit order.

Q = np.zeros((4, 4))  # upper triangular, for A = A_used
offset = 0.0

best_jobs = []  # the feasible choice of lowest total cost, as a list of job indices
best_value = 0  # its total value

A_min = 0.0  # smallest weight in penalties for which the feasible optimum is the unique ground state

h = np.zeros(4)  # Ising fields for A = A_used
J = np.zeros((4, 4))  # Ising couplings, upper triangular
const = 0.0

# Anneal H(s) = (1 - s) H_B + s H_P / (largest |coefficient| of h and J), s = t / T.
success = []  # probability of the feasible optimum for each T in T_values, with A_used
success_big = []  # the same with A_big

jobs = []  # the jobs the anneal at T = 80 most probably selects
