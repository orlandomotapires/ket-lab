import pennylane as qml

# Already defined: prepare_input() prepares |ψ⟩ on qubit 0, and inject_error() applies the
# error chosen with the buttons to the data qubits 0, 1 and 2. Qubits 3 and 4 are the ancillas.
dev = qml.device("default.mixed", wires=5)


def encode():
    # α|0⟩ + β|1⟩  ->  α|000⟩ + β|111⟩
    pass


def recover():
    # 1. Store the syndrome in ancillas 3 and 4.
    # 2. Correct with Toffoli gates controlled by the ancillas (no measurement).
    pass


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
