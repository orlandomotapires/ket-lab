import itertools

L = 3


def plaquette_edges(L, r, c):
    # The four edges of plaquette (r, c); indices wrap around the torus.
    return [("h", r, c), ("h", (r + 1) % L, c), ("v", r, c), ("v", r, (c + 1) % L)]


def defects(L, chain):
    found = []
    for r in range(L):
        for c in range(L):
            count = sum(1 for edge in plaquette_edges(L, r, c) if edge in chain)
            if count % 2 == 1:
                found.append((r, c))
    return found


def logical_class(L, chain):
    a = sum(1 for e in chain if e[0] == "h" and e[1] == 0) % 2
    b = sum(1 for e in chain if e[0] == "v" and e[2] == 0) % 2
    return (a, b)


chain = {("v", 0, 1), ("v", 0, 2)}
print(defects(L, chain))

edges = [(t, r, c) for t in "hv" for r in range(L) for c in range(L)]
distance = None
for size in range(1, len(edges) + 1):
    for candidate in itertools.combinations(edges, size):
        chain = set(candidate)
        if not defects(L, chain) and logical_class(L, chain) != (0, 0):
            distance = size
            break
    if distance is not None:
        break
