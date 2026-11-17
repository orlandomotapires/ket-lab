# Idea: with at most two X errors, a correction of minimum weight never needs more than two edges, so
# trying every chain of 0, 1 and 2 edges in that order finds one. The correction removes the defects
# either way; whether the error succeeded in fooling the code is decided by the loop error + correction.
import itertools

L = 3


def plaquette_edges(L, r, c):
    # The four edges of plaquette (r, c); indices wrap around the torus (lesson mission).
    return [("h", r, c), ("h", (r + 1) % L, c), ("v", r, c), ("v", r, (c + 1) % L)]


def defects(L, chain):
    # Plaquettes with an odd number of chain edges (lesson mission).
    return [(r, c) for r in range(L) for c in range(L)
            if sum(1 for edge in plaquette_edges(L, r, c) if edge in chain) % 2 == 1]


def logical_class(L, chain):
    # Parity of the chain on the row of h edges and on the column of v edges (lesson mission).
    a = sum(1 for e in chain if e[0] == "h" and e[1] == 0) % 2
    b = sum(1 for e in chain if e[0] == "v" and e[2] == 0) % 2
    return (a, b)


EDGES = [(t, r, c) for t in "hv" for r in range(L) for c in range(L)]


def decode(L, found):
    # Going through the sizes in increasing order makes the first chain that reproduces the defects
    # a chain of minimum weight; a decoder that picks the first match of any size would not be minimal.
    for size in range(0, 4):
        for candidate in itertools.combinations(EDGES, size):
            if sorted(defects(L, set(candidate))) == sorted(found):
                return set(candidate)
    return None


def outcome(L, error, correction):
    # error and correction have the same defects, so their symmetric difference has none:
    # it is a product of stabilizers (class (0, 0)) or a logical operator (any other class).
    residual = set(error) ^ set(correction)
    return "success" if logical_class(L, residual) == (0, 0) else "failure"


failures = 0
total = 0
# Every pair of distinct edges is one hidden error of two X flips.
for pair in itertools.combinations(EDGES, 2):
    error = set(pair)
    total += 1
    # The decoder only sees the defects, never the error itself.
    correction = decode(L, defects(L, error))
    if outcome(L, error, correction) == "failure":
        failures += 1
print(failures, "of", total)
