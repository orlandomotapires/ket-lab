# Idea: an extrapolation is a weighted sum of the measured values. Its shot noise is the noise of
# one point times the length of the weight vector, and its bias is how far the same sum lands from
# the ideal value when it is fed with exact, noiseless-of-shots values. Compare sqrt(bias² + noise²).
import numpy as np

scales = [1, 3, 5]
exact = [deep_expectation(s) for s in scales]


def at_zero(degree, y):
    # The polynomial's coefficients are a fixed linear map of y; the last one is the value at scale 0.
    # Its row of the map is the list of weights that multiply the three points.
    weights = np.linalg.pinv(np.vander(scales, degree + 1))[-1]
    return weights @ np.asarray(y), weights


# The estimates come from what the device measured.
zne_lin, w_lin = at_zero(1, measured)
zne_quad, w_quad = at_zero(2, measured)

# Independent errors of equal size add in quadrature, each scaled by its weight.
sigma_lin = sigma * np.sqrt(np.sum(w_lin**2))
sigma_quad = sigma * np.sqrt(np.sum(w_quad**2))

# The bias does not depend on shots: it is what the method gets wrong with infinitely many of them.
bias_lin = at_zero(1, exact)[0] - ideal
bias_quad = at_zero(2, exact)[0] - ideal

# Bias and shot noise are independent, so the expected squared errors add.
total_lin = np.hypot(bias_lin, sigma_lin)
total_quad = np.hypot(bias_quad, sigma_quad)
best = "linear" if total_lin < total_quad else "quadratic"
print(bias_lin, sigma_lin, total_lin, "|", bias_quad, sigma_quad, total_quad, "->", best)
