import pennylane as qml

# Already available: prepare_input() prepares |ψ⟩ on qubit 0, and inject_error() applies the
# error chosen with the buttons (data qubits 0, 1 and 2). Ancillas: qubits 3 and 4.
dev = qml.device("default.mixed", wires=5)


def encode():
    # α|0⟩ + β|1⟩  ->  α|000⟩ + β|111⟩
    pass


def recover():
    # 1. Syndrome on ancillas 3 and 4.
    # 2. Correction with Toffoli, without measuring.
    pass


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
