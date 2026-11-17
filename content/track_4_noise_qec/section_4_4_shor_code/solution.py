# Idea: concatenate the two codes. The phase-flip code on the block leaders protects against Z,
# and a bit-flip code inside each block protects against X. Decoding is the encoding reversed,
# with a Toffoli gate as the majority vote at each level.
import pennylane as qml

dev = qml.device("default.mixed", wires=9)

BLOCKS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]


def encode():
    # Phase-flip code on the leaders: |ψ⟩ -> α|+++⟩ + β|−−−⟩.
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[0, 6])
    for leader in (0, 3, 6):
        qml.Hadamard(wires=leader)
    # Bit-flip code in each block: |0⟩ -> |000⟩, |1⟩ -> |111⟩, so |+⟩ -> (|000⟩ + |111⟩)/√2.
    for a, b, c in BLOCKS:
        qml.CNOT(wires=[a, b])
        qml.CNOT(wires=[a, c])


def decode():
    # Inner decoding: after the CNOT gates, qubits b and c hold the syndrome of the block,
    # and the Toffoli gate flips the leader a exactly when both are 1 (a flip of a).
    # A flip of b or c leaves the leader unchanged, as required.
    # A Z anywhere in the block ends up as a Z on the leader, for the outer code to handle.
    for a, b, c in BLOCKS:
        qml.CNOT(wires=[a, b])
        qml.CNOT(wires=[a, c])
        qml.Toffoli(wires=[b, c, a])
    # Outer decoding: the Hadamard turns a phase flip of a block into a bit flip of its leader,
    # and the same three gates vote on the leaders.
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
    # After decoding, qubit 0 holds |ψ⟩ again; the other qubits hold the syndrome.
    return qml.density_matrix(wires=[0])
