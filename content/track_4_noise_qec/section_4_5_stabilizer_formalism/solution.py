# Idea: Pauli strings commute exactly when they anticommute on an even number of positions,
# and the syndrome bit of an error is 1 for each generator that it anticommutes with.
# Generators of the three-qubit bit-flip code, as Pauli strings (qubits 1, 2, 3 from left to right).
STABILIZERS = ["ZZI", "IZZ"]


def commutes(a, b):
    # Each position where both Paulis are non-identity and different contributes a factor −1.
    # Identity or equal Paulis commute, so they add nothing.
    clashes = sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y)
    # The signs multiply, so the strings commute exactly when the number of −1 factors is even.
    return clashes % 2 == 0


def syndrome(error, stabilizers):
    # g E|ψ⟩ = ±E g|ψ⟩: the damaged state has eigenvalue −1 for g exactly when E anticommutes with g.
    return tuple(0 if commutes(error, g) else 1 for g in stabilizers)


# One X, Y or Z at each of the three positions, with I elsewhere.
ERRORS = [
    "I" * i + pauli + "I" * (2 - i)
    for i in range(3)
    for pauli in "XYZ"
]

table = {error: syndrome(error, STABILIZERS) for error in ERRORS}

# X̄ = XXX flips all three qubits, so it maps |000⟩ to |111⟩ and commutes with both generators.
logical_X = "XXX"
# Z̄ = Z on one qubit gives +1 on |000⟩ and −1 on |111⟩, and anticommutes with X̄.
# It commutes with the generators but is not a product of them.
logical_Z = "ZII"
