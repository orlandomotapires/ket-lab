# Idea: one level of the code maps p to f(p) = 3p² − 2p³, and concatenation applies the map again
# to its own output. The pseudo-threshold is the fixed point of f, and the number of levels needed
# comes from iterating f until the target is reached.
def f(p):
    # The code fails when two or three qubits flip: 3p²(1 − p) + p³.
    return 3 * p**2 - 2 * p**3


def concatenated(p, k):
    # Each level encodes every qubit of the level below, so its error rate is f of the previous one.
    for _ in range(k):
        p = f(p)
    return p


def generic_rate(p, c, k):
    # Solution of p_k = c·p_{k-1}² with p_0 = p: the exponent doubles at each level.
    return (c * p) ** (2**k) / c


# The fixed point f(p) = p, with 0 < p < 1: 2p² − 3p + 1 = (2p − 1)(p − 1) = 0 gives p = 1/2.
p_th = 0.5


def levels_needed(p, target):
    # Above the pseudo-threshold f(p) > p, so more levels only make the error rate worse.
    if p >= p_th:
        return None
    k = 0
    # Below the pseudo-threshold the rate falls at every level, so the loop ends.
    while concatenated(p, k) > target:
        k += 1
    return k


p = 0.01
target = 1e-15

k_needed = levels_needed(p, target)
# Each level replaces every qubit by three, so k levels use 3^k physical qubits.
qubits = 3**k_needed
