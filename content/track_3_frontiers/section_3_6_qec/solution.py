import pennylane as qml

dev = qml.device("default.mixed", wires=5)


def encode():
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])


def recover():
    # Síndrome: ancilla 3 = paridade dos qubits 0 e 1; ancilla 4 = paridade de 1 e 2.
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[1, 4])
    qml.CNOT(wires=[2, 4])
    # Correção: (a3, a4) = (1, 0) -> X no 0; (1, 1) -> X no 1; (0, 1) -> X no 2.
    qml.PauliX(wires=4)
    qml.Toffoli(wires=[3, 4, 0])
    qml.PauliX(wires=4)
    qml.Toffoli(wires=[3, 4, 1])
    qml.PauliX(wires=3)
    qml.Toffoli(wires=[3, 4, 2])
    qml.PauliX(wires=3)


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
