import itertools

# The logical problem of lessons 6.2 and 6.3: three spins, a triangle of couplings.
h = [1 / 3, 2 / 3, 1]
J = {(0, 1): 1 / 6, (0, 2): 1 / 4, (1, 2): 1 / 2}

# The hardware: four qubits on a square. These are its only edges (there is no 0-2 and no 1-3).
edges = [(0, 1), (1, 2), (2, 3), (0, 3)]


def embed(F):
    # Return (fields, couplings) for chain strength F.
    # Logical qubit 2 becomes the chain of physical qubits 2 and 3, coupled by -F Z2 Z3.
    # fields: list of 4 numbers. couplings: dict {(i, j): value} with i < j.
    fields = [0, 0, 0, 0]
    couplings = {}
    return fields, couplings


def energy(s, fields, couplings):
    # Energy of the physical spin state s = (s0, s1, s2, s3).
    return 0


F_values = [0.1, 0.2, 0.4, 0.8]

# For each F in F_values: is the chain intact in the lowest-energy state,
# and which logical spins (s0, s1, s2) does that state decode to (None if the chain is broken)?
chain_intact = []
decoded = []

# The smallest F in F_values whose ground state has an intact chain and decodes to (+1, -1, -1).
F_min = None
