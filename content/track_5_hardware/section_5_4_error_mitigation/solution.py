# Idea: readout error is linear, so invert it. Gate noise grows with the folding scale, so measure at
# several scales and extend the fitted curve back to scale 0.
import numpy as np

# Part 1: p_meas = A p_true, so solving the linear system undoes the readout error.
# Then ⟨Z⟩ = P(0) − P(1) of the corrected distribution.
p_true = np.linalg.solve(A, p_meas)
z_readout = p_true[0] - p_true[1]

# Part 2: folding G as G G† G leaves the ideal result unchanged and multiplies the noise by 1, 3, 5.
scales = [1, 3, 5]
values = [noisy_expectation(s) for s in scales]
# A straight line through (scale, value), evaluated at scale 0, estimates the noiseless value.
coefficients = np.polyfit(scales, values, 1)
zne = np.polyval(coefficients, 0)
