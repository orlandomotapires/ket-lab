import itertools
import numpy as np

# Given: one spin per number, cost E(s) = (a · s)²
a = np.array([4, 5, 6, 7, 8])

# Replace each placeholder with your computation
J = np.zeros((5, 5))                # couplings J[i, j] for i < j, zeros elsewhere
energies = np.zeros(32)             # E(s) for the 32 states, in the order of itertools.product([1, -1], repeat=5)
ground_energy = 0                   # lowest energy
ground_states = np.zeros((1, 5))    # rows of +1/-1 with the lowest energy
Q = np.zeros((5, 5))                # upper triangular QUBO matrix, with s = 1 - 2x
offset = 0                          # constant of the QUBO
