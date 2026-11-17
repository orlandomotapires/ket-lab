# Idea: SPSA estimates the whole gradient from two evaluations, so 60 steps cost about 120 circuit runs.
import numpy as np

rng = np.random.default_rng(7)
params = np.array([0.4, 1.2, 0.3, 0.8])
energies = [cost(params)]

for step in range(1, 61):
    # Gain sequences shrink with the step: large moves first, fine moves at the end.
    a = 0.6 / step**0.602
    c = 0.2 / step**0.101
    # One random direction of ±1 per angle: all angles are perturbed together.
    delta = rng.choice([-1.0, 1.0], size=params.size)
    # Two evaluations give the slope along that direction, whatever the number of angles.
    slope = (cost(params + c * delta) - cost(params - c * delta)) / (2 * c)
    # Move against the estimated gradient, using the same sign pattern.
    params = params - a * slope * delta
    energies.append(cost(params))
