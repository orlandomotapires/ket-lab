import numpy as np

# Part 1: solve A p_true = p_meas, then ⟨Z⟩ = P(0) − P(1).
p_true = np.linalg.solve(A, p_meas)
z_readout = p_true[0] - p_true[1]

# Part 2: fit the values against the noise scale and read the fit at scale 0.
scales = [1, 3, 5]
values = [noisy_expectation(s) for s in scales]
coefficients = np.polyfit(scales, values, 1)
zne = np.polyval(coefficients, 0)
