import pennylane as qml

# Already defined: prepare_input() prepares |ψ⟩ on qubit 0, and inject_error() applies the
# error chosen with the buttons to any of the nine qubits. The three blocks are
# (0, 1, 2), (3, 4, 5) and (6, 7, 8); the block leaders are qubits 0, 3 and 6.
dev = qml.device("default.mixed", wires=9)


def encode():
    # |ψ⟩ -> the phase-flip code on the leaders 0, 3, 6, then
    # each leader -> a bit-flip code on its block.
    pass


def decode():
    # 1. Undo the bit-flip code in each block and correct a bit flip by majority vote.
    # 2. Undo the phase-flip code on the leaders and correct a phase flip by majority vote.
    # Afterwards qubit 0 must hold |ψ⟩ again.
    pass


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    decode()
    return qml.density_matrix(wires=[0])
