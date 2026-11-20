# Idea: a code with more qubits can fail in more ways. If any two of 7 errors are fatal, there are
# 21 pairs instead of 3, so one level maps p to about 21p² and the break-even point falls from 1/2
# to about 0.058. The threshold has no tidy closed form, so bisection finds it, and the same
# iteration as in the mission counts the levels.
def f(p):
    # One level of the three-qubit code, from the mission.
    return 3 * p**2 - 2 * p**3


def f7(p):
    # The block survives with no error or with exactly one; every other count of errors is a failure.
    return 1 - (1 - p) ** 7 - 7 * p * (1 - p) ** 6


def fixed_point(step, lo, hi):
    # Bisection on step(p) − p. Below the threshold a level lowers p, so the sign is negative at lo
    # and positive at hi, and the sign change brackets the fixed point.
    for _ in range(200):
        mid = (lo + hi) / 2
        if step(mid) - mid < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def levels_for(step, p, target):
    k = 0
    while p > target:
        nxt = step(p)
        # If a level does not lower the error rate, more levels never will: stop with None.
        if nxt >= p:
            return None
        p = nxt
        k += 1
    return k


# The threshold sits between 0.01 (a level helps) and 0.5 (a level hurts).
p7_th = fixed_point(f7, 0.01, 0.5)
k7 = levels_for(f7, 1e-3, 1e-15)
# Each level replaces every qubit by seven.
qubits7 = 7**k7
# The same count for the three-qubit code, to compare.
k3 = levels_for(f, 1e-3, 1e-15)
print(p7_th, k7, qubits7, k3, 3**k3)
