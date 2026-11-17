import numpy as np

# Already defined: cost(params) returns -F for a 4-angle ansatz (F is the fidelity with |Φ⁺⟩),
# and cost.calls counts how many times the circuit has been evaluated.
rng = np.random.default_rng(7)
params = np.array([0.4, 1.2, 0.3, 0.8])
energies = [cost(params)]

# Minimize the cost with SPSA: each step perturbs all angles at once, so it needs
# only 2 evaluations, however many parameters there are. Use at most 200 evaluations
# in total and finish with a cost of -0.97 or lower.
for step in range(1, 61):
    pass
