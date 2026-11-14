# Generators of the three-qubit bit-flip code, as Pauli strings (qubits 1, 2, 3 from left to right).
STABILIZERS = ["ZZI", "IZZ"]


def commutes(a, b):
    # Anticommuting positions: both non-identity and different.
    clashes = sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y)
    return clashes % 2 == 0


def syndrome(error, stabilizers):
    return tuple(0 if commutes(error, g) else 1 for g in stabilizers)


ERRORS = [
    "I" * i + pauli + "I" * (2 - i)
    for i in range(3)
    for pauli in "XYZ"
]

table = {error: syndrome(error, STABILIZERS) for error in ERRORS}

logical_X = "XXX"
logical_Z = "ZII"
