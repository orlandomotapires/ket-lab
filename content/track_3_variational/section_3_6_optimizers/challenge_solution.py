# Idea: parameter shift needs 2 evaluations for each of the 12 angles, 24 per step, so 200 evaluations
# allow 8 steps. SPSA needs 2 per step whatever the number of angles, so the same budget gives 95 steps.
# On this cost the 8 exact gradients cannot get far, and the 95 noisy ones can.
import numpy as np


# 1. Parameter-shift gradient descent, 8 steps of 24 evaluations each (192 of the 200).
def shift_gradient(params):
    grad = np.zeros(12)
    for k in range(12):
        # A shift of π/2 on one RY angle gives the exact derivative: two evaluations per angle.
        shift = np.zeros(12)
        shift[k] = np.pi / 2
        grad[k] = (cost_ps(params + shift) - cost_ps(params - shift)) / 2
    return grad


params_ps = np.array(theta0, dtype=float)
for step in range(8):
    # The step size is fixed by hand: much larger values make the cost jump around.
    params_ps = params_ps - 0.3 * shift_gradient(params_ps)

# 2. SPSA from the same start, 95 steps of 2 evaluations each (190 of the 200).
rng = np.random.default_rng(7)
params_spsa = np.array(theta0, dtype=float)
for step in range(1, 96):
    # Gain sequences shrink with the step: large moves first, fine moves at the end.
    a = 0.4 / step**0.602
    c = 0.2 / step**0.101
    # One random sign per angle: all 12 angles are perturbed together, so the slope costs 2 evaluations.
    delta = rng.choice([-1.0, 1.0], size=12)
    slope = (cost_spsa(params_spsa + c * delta) - cost_spsa(params_spsa - c * delta)) / (2 * c)
    # Step against the estimated gradient, with the same sign pattern.
    params_spsa = params_spsa - a * slope * delta

# One more evaluation each to read the final costs (the counters stay far below 200).
print(cost_ps(params_ps), cost_spsa(params_spsa), cost_ps.calls, cost_spsa.calls)
