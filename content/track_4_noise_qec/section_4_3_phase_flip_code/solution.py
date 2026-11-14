import pennylane as qml

dev = qml.device("default.mixed", wires=5)


def hadamards():
    for wire in range(3):
        qml.Hadamard(wires=wire)


def encode():
    # Bit-flip encoding, then a Hadamard on each qubit: α|000⟩ + β|111⟩ -> α|+++⟩ + β|−−−⟩.
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])
    hadamards()


def recover():
    # In the Hadamard basis a phase flip is a bit flip, so the bit-flip recovery applies.
    hadamards()
    # Syndrome: ancilla 3 = parity of qubits 0 and 1; ancilla 4 = parity of 1 and 2.
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[1, 4])
    qml.CNOT(wires=[2, 4])
    # Correction: (a3, a4) = (1, 0) -> flip 0; (1, 1) -> flip 1; (0, 1) -> flip 2.
    qml.PauliX(wires=4)
    qml.Toffoli(wires=[3, 4, 0])
    qml.PauliX(wires=4)
    qml.Toffoli(wires=[3, 4, 1])
    qml.PauliX(wires=3)
    qml.Toffoli(wires=[3, 4, 2])
    qml.PauliX(wires=3)
    # Back to the code space.
    hadamards()


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
