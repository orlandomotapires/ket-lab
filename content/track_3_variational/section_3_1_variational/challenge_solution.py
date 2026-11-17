# Idea: f(θ) = a cos θ + b sin θ + c has three unknowns, so three runs of the circuit fix it.
# The minimum of a cos θ + b sin θ is at the direction opposite to the vector (a, b), so no
# gradient descent is needed: the angle comes from a formula.
import numpy as np


def recover(f):
    # f(0) = a + c, f(π/2) = b + c and f(−π/2) = −b + c: three equations, three unknowns.
    f0 = f(0.0)
    f_plus = f(np.pi / 2)
    f_minus = f(-np.pi / 2)
    # Adding the last two cancels b, subtracting them cancels c.
    c = (f_plus + f_minus) / 2
    b = (f_plus - f_minus) / 2
    # Then f(0) gives a.
    a = f0 - c
    # a cos θ + b sin θ = R cos(θ − φ) with φ = atan2(b, a); the minimum is at φ + π.
    theta_star = np.arctan2(-b, -a)
    return a, b, c, theta_star


# Testing on the visible circuit: the minimum value is c − sqrt(a² + b²).
a, b, c, theta_star = recover(lambda t: float(mystery(t)))
print(a, b, c, theta_star, float(mystery(theta_star)))
