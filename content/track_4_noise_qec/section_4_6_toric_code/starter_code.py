import itertools

L = 3


def plaquette_edges(L, r, c):
    # The four edges of plaquette (r, c); indices wrap around the torus.
    return [("h", r, c), ("h", (r + 1) % L, c), ("v", r, c), ("v", r, (c + 1) % L)]


def defects(L, chain):
    # Plaquettes (r, c) with an odd number of edges in the chain.
    return []


def logical_class(L, chain):
    # (a, b): parity of the chain's edges in the row ("h", 0, c) and in the column ("v", r, 0).
    return (0, 0)


# Example: X errors on two neighbouring vertical edges in the same row.
chain = {("v", 0, 1), ("v", 0, 2)}
print(defects(L, chain))

# Size of the smallest chain with no defects and logical_class other than (0, 0).
distance = 0
