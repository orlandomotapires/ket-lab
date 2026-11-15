import pennylane as qml

# Already defined: prepare_input() prepares |ψ⟩ on qubit 0, and inject_error() applies the
# error chosen with the buttons. The blocks are (0, 1, 2), (3, 4, 5), (6, 7, 8); the leaders are 0, 3, 6.
dev = qml.device("default.mixed", wires=9)


def encode():
    # Phase-flip code on the leaders, then a bit-flip code in each block (lesson 4.4).
    pass


def decode():
    # Majority vote in each block, then on the leaders (lesson 4.4).
    pass


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    decode()
    return qml.density_matrix(wires=[0])


def logical_pauli(error):
    # error: list of nine letters from "IXYZ", error[q] acts on qubit q.
    # Return "I", "X", "Y" or "Z": the Pauli left on the logical qubit after decoding.
    return "I"


def logical_failure(p):
    # Probability that logical_pauli is not "I" when every qubit is I with probability 1 - p
    # and X, Y, Z with probability p / 3 each.
    return 0.0


def bare_failure(p):
    # An unprotected qubit under the same channel.
    return 0.0


# The smallest p > 0 with logical_failure(p) = bare_failure(p).
p_star = 0.0
