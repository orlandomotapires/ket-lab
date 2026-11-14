def f(p):
    # Logical error probability of one level of the three-qubit code: 3p² − 2p³.
    return p


def concatenated(p, k):
    # Error probability after k levels of concatenation: f applied k times.
    return p


def generic_rate(p, c, k):
    # The model (c·p)^(2^k) / c.
    return p


def levels_needed(p, target):
    # Smallest k with concatenated(p, k) <= target, or None if it never gets there.
    return 0


# Threshold: the value 0 < p < 1 with f(p) = p.
p_th = 0.0

p = 0.01
target = 1e-15

# Levels needed to go from p to target, and physical qubits per logical qubit (3 per level).
k_needed = 0
qubits = 1
