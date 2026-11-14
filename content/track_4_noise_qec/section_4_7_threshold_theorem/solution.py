def f(p):
    return 3 * p**2 - 2 * p**3


def concatenated(p, k):
    for _ in range(k):
        p = f(p)
    return p


def generic_rate(p, c, k):
    return (c * p) ** (2**k) / c


p_th = 0.5


def levels_needed(p, target):
    if p >= p_th:
        return None
    k = 0
    while concatenated(p, k) > target:
        k += 1
    return k


p = 0.01
target = 1e-15

k_needed = levels_needed(p, target)
qubits = 3**k_needed
