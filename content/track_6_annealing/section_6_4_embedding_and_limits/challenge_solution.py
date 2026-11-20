import itertools

# Idea: the chain holds once the intact ground state is strictly below every broken state, and that
# condition only gets easier as F grows (intact energies fall by F, broken ones rise by F). A
# monotone yes/no question has a single switching point, which bisection finds to any precision.


def min_chain_strength(h, J):
    def energy(s, F):
        # The embedding of the mission for any h and J: the same four terms as embed(F) gave.
        return (h[0] * s[0] + h[1] * s[1] + h[2] * s[2]
                + J[(0, 1)] * s[0] * s[1] + J[(1, 2)] * s[1] * s[2]
                + J[(0, 2)] * s[0] * s[3] - F * s[2] * s[3])

    def holds(F):
        energies = sorted((energy(s, F), s) for s in itertools.product([1, -1], repeat=4))
        low = energies[0][0]
        # A tie with a broken state counts as broken: the sampler could return either.
        return all(s[2] == s[3] for e, s in energies if e < low + 1e-9)

    # The thresholds of these problems are below 2, so 4 is safely on the intact side.
    lo, hi = 0.0, 4.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if holds(mid):
            hi = mid  # the chain holds at mid, so the threshold is at or below it
        else:
            lo = mid  # the chain breaks at mid, so the threshold is above it
    return round(hi, 4)


h = [1 / 3, 2 / 3, 1]
J = {(0, 1): 1 / 6, (0, 2): 1 / 4, (1, 2): 1 / 2}

# Testing on the problem of the lesson: the threshold is 1/6.
print(min_chain_strength(h, J))
