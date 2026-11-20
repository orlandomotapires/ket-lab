# Idea: write one function that runs the Shor code for a list of errors and says whether qubit 0
# came back, then scan all the pairs. Two X errors defeat the inner vote of the block they share,
# two Z errors defeat the outer vote unless they sit in the same block, where they cancel.
import itertools

import pennylane as qml

dev = qml.device("default.mixed", wires=9)
pure = qml.device("default.qubit", wires=9)

BLOCKS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]


def encode():
    # Phase-flip code on the leaders, then a bit-flip code in each block.
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[0, 6])
    for leader in (0, 3, 6):
        qml.Hadamard(wires=leader)
    for a, b, c in BLOCKS:
        qml.CNOT(wires=[a, b])
        qml.CNOT(wires=[a, c])


def decode():
    # The encoding reversed, with a Toffoli gate as the majority vote at each level.
    for a, b, c in BLOCKS:
        qml.CNOT(wires=[a, b])
        qml.CNOT(wires=[a, c])
        qml.Toffoli(wires=[b, c, a])
    for leader in (0, 3, 6):
        qml.Hadamard(wires=leader)
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[0, 6])
    qml.Toffoli(wires=[3, 6, 0])


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    decode()
    return qml.density_matrix(wires=[0])


@qml.qnode(pure)
def logical_y(errors):
    # |+i⟩ is the +1 eigenstate of Y. A logical X and a logical Z both turn it into |-i⟩, so
    # either kind of failure flips the sign of ⟨Y⟩ (a single state like |0⟩ or |+⟩ would miss one).
    qml.Hadamard(wires=0)
    qml.S(wires=0)
    encode()
    for qubit, kind in errors:
        if kind == "X":
            qml.PauliX(wires=qubit)
        else:
            qml.PauliZ(wires=qubit)
    decode()
    return qml.expval(qml.PauliY(0))


def survives(errors):
    # ⟨Y⟩ is exactly 1 when the state is back and exactly -1 after a logical X or Z.
    return bool(logical_y(errors) > 0.999)


pairs = list(itertools.combinations(range(9), 2))
# Unordered pairs for equal letters, since XiXj and XjXi are the same error.
bad_xx = [(i, j) for i, j in pairs if not survives([(i, "X"), (j, "X")])]
bad_zz = [(i, j) for i, j in pairs if not survives([(i, "Z"), (j, "Z")])]
# X and Z are different errors, so the order of the pair matters: X on i and Z on j.
bad_xz = [(i, j) for i in range(9) for j in range(9) if i != j and not survives([(i, "X"), (j, "Z")])]
