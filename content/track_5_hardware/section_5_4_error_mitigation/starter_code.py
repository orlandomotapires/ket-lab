import numpy as np

# The lesson provides:
#   A                      the assignment matrix, A[i, j] = P(read i | true j)
#   p_meas                 the measured frequencies of 0 and 1
#   noisy_expectation(s)   ⟨Z⟩ of the noisy circuit with the noise scaled by s = 1, 3, 5, ...
# The exact ⟨Z⟩ of the circuit is cos(0.9), and the exact ⟨Z⟩ of the measured state is 0.6.

# Part 1: readout mitigation. Recover the true distribution from p_meas.
z_readout = p_meas[0] - p_meas[1]  # unmitigated

# Part 2: zero-noise extrapolation.
scales = [1, 3, 5]
values = [noisy_expectation(s) for s in scales]
zne = values[0]  # unmitigated
