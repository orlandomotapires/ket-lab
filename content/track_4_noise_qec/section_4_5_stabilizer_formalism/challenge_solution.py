# Idea: the Steane code is built from one parity-check matrix H: each row gives an X-type generator
# (X where the row has a 1) and a Z-type generator. Because H has the columns 1 to 7 in binary,
# the syndrome of a single-qubit error spells out which qubit was hit, and no weight-2 operator is
# a logical one.
import itertools

HAMMING = [
    [0, 0, 0, 1, 1, 1, 1],
    [0, 1, 1, 0, 0, 1, 1],
    [1, 0, 1, 0, 1, 0, 1],
]


def commutes(a, b):
    # Anticommuting positions are those where both are non-identity and different (lesson mission).
    clashes = sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y)
    return clashes % 2 == 0


def syndrome(error, stabilizers):
    return tuple(0 if commutes(error, g) else 1 for g in stabilizers)


def css_generators(H):
    # One generator per row and per letter: the X-type ones come first, then the Z-type ones.
    x_type = ["".join("X" if bit else "I" for bit in row) for row in H]
    z_type = ["".join("Z" if bit else "I" for bit in row) for row in H]
    return x_type + z_type


def css_valid(H):
    # The generators define a code only if they all commute: an X-type and a Z-type generator
    # commute when their rows overlap in an even number of positions.
    gens = css_generators(H)
    return all(commutes(a, b) for a, b in itertools.combinations(gens, 2))


STEANE = css_generators(HAMMING)
print(css_valid(HAMMING))

# Each single-qubit error has its own syndrome, so a table from syndrome to error is a decoder.
LOOKUP = {}
for position in range(7):
    for pauli in "XYZ":
        error = "I" * position + pauli + "I" * (6 - position)
        LOOKUP[syndrome(error, STEANE)] = (position, pauli)


def locate(bits):
    return LOOKUP[tuple(bits)]


# A logical operator commutes with every generator but is not in the group. Such an operator
# anticommutes with the logical X or the logical Z, which both are on all seven qubits for this code.
logical_X = "XXXXXXX"
logical_Z = "ZZZZZZZ"
min_logical = None
distance = None
# Searching by increasing weight, the first hit has the smallest weight.
for weight in range(1, 8):
    for positions in itertools.combinations(range(7), weight):
        for letters in itertools.product("XYZ", repeat=weight):
            candidate = ["I"] * 7
            for position, letter in zip(positions, letters):
                candidate[position] = letter
            candidate = "".join(candidate)
            detected = any(not commutes(candidate, g) for g in STEANE)
            acts_on_code = not commutes(candidate, logical_X) or not commutes(candidate, logical_Z)
            if not detected and acts_on_code:
                min_logical = candidate
                distance = weight
                break
        if distance:
            break
    if distance:
        break
print(min_logical, distance)
