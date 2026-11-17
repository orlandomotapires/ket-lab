# Generators of the three-qubit bit-flip code, as Pauli strings (qubits 1, 2, 3 from left to right).
STABILIZERS = ["ZZI", "IZZ"]


def commutes(a, b):
    # True when the Pauli strings a and b commute: they anticommute on an even number of positions.
    return True


def syndrome(error, stabilizers):
    # A tuple with one bit per generator: 0 if error commutes with it, 1 if it anticommutes.
    return ()


# The nine single-qubit errors: "XII", "YII", "ZII", "IXI", ..., "IIZ".
ERRORS = [
    "I" * i + pauli + "I" * (2 - i)
    for i in range(3)
    for pauli in "XYZ"
]

# table[error] = syndrome of that error for STABILIZERS.
table = {}

# Pauli strings that act as X and Z on the encoded qubit.
logical_X = "III"
logical_Z = "III"
