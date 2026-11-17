import itertools

# Idea: logical qubit 2 is coupled to both 0 and 1, which closes a triangle that the square
# cannot hold. Split qubit 2 into a chain of two physical qubits, 2 and 3, each carrying one
# of its couplings, and glue them with a ferromagnetic coupling -F Z2 Z3. The chain is
# faithful only when its ground state has s2 = s3, so we scan F to see where that starts.

h = [1 / 3, 2 / 3, 1]
J = {(0, 1): 1 / 6, (0, 2): 1 / 4, (1, 2): 1 / 2}

# The hardware: four qubits on a square, with no edge 0-2 or 1-3.
edges = [(0, 1), (1, 2), (2, 3), (0, 3)]


def embed(F):
    # All of h2 goes on physical qubit 2: it is the logical field, counted once.
    # Splitting it in half would make the field cancel when the chain breaks.
    fields = [h[0], h[1], h[2], 0]
    couplings = {
        (0, 1): J[(0, 1)],   # an edge that exists, so J01 stays where it was
        (1, 2): J[(1, 2)],   # qubit 2 keeps its coupling to qubit 1
        (0, 3): J[(0, 2)],   # qubit 3 takes the coupling to qubit 0, on the edge 3-0
        (2, 3): -F,          # negative sign: aligned chain spins have lower energy
    }
    return fields, couplings


def energy(s, fields, couplings):
    # Same classical Ising energy as before, over the physical spins and hardware edges.
    return (sum(c * s[i] * s[j] for (i, j), c in couplings.items())
            + sum(f * x for f, x in zip(fields, s)))


F_values = [0.1, 0.2, 0.4, 0.8]

chain_intact = []
decoded = []
for F in F_values:
    fields, couplings = embed(F)
    # Brute force over all 16 states: small enough that nothing needs to be approximated.
    ground = min(itertools.product([1, -1], repeat=4),
                 key=lambda s: energy(s, fields, couplings))
    intact = ground[2] == ground[3]
    chain_intact.append(intact)
    # A broken chain has no single value for logical qubit 2, so we do not decode it.
    decoded.append(ground[:3] if intact else None)

# The first listed F that keeps the chain and gives the true logical ground state.
F_min = next((F for F, d in zip(F_values, decoded) if d == (1, -1, -1)), None)
