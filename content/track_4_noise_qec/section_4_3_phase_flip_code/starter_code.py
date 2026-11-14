import pennylane as qml

# Already defined: prepare_input() prepares |ψ⟩ on qubit 0, and inject_error() applies the
# error chosen with the buttons to the data qubits 0, 1 and 2. Qubits 3 and 4 are the ancillas.
dev = qml.device("default.mixed", wires=5)


def encode():
    # α|0⟩ + β|1⟩  ->  α|+++⟩ + β|−−−⟩
    pass


def recover():
    # 1. Change basis so that a phase flip becomes a bit flip.
    # 2. Store the syndrome in ancillas 3 and 4 and correct with Toffoli gates.
    # 3. Change basis back, so that the data qubits are in the code space again.
    pass


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
