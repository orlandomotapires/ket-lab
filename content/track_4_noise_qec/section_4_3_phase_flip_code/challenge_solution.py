# Idea: S X S† = Y, so the bit-flip code with an S gate on every qubit corrects Y errors. A Y
# on a qubit in the S frame is an X on that qubit in the bit-flip frame (Y S = S X), and the
# bit-flip recovery already fixes that.
import pennylane as qml

dev = qml.device("default.mixed", wires=5)


def phase_gates():
    # S takes X to Y by conjugation: S X S† = Y.
    for wire in range(3):
        qml.S(wires=wire)


def unphase_gates():
    # S† undoes the frame change; without it the bit-flip recovery would see the wrong basis.
    for wire in range(3):
        qml.adjoint(qml.S(wires=wire))


def encode():
    # Bit-flip encoding, then S on each qubit: α|000⟩ + β|111⟩ -> α|000⟩ - iβ|111⟩.
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])
    phase_gates()


def recover():
    # Y S = S X, so after S† a Y error has become an X error (up to a global phase).
    unphase_gates()
    # Syndrome: ancilla 3 = parity of qubits 0 and 1; ancilla 4 = parity of 1 and 2.
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[1, 4])
    qml.CNOT(wires=[2, 4])
    # Correction by deferred measurement: (1, 0) -> flip 0; (1, 1) -> flip 1; (0, 1) -> flip 2.
    qml.PauliX(wires=4)
    qml.Toffoli(wires=[3, 4, 0])
    qml.PauliX(wires=4)
    qml.Toffoli(wires=[3, 4, 1])
    qml.PauliX(wires=3)
    qml.Toffoli(wires=[3, 4, 2])
    qml.PauliX(wires=3)
    # Back to the code space, which is where encode left the data qubits.
    phase_gates()


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
