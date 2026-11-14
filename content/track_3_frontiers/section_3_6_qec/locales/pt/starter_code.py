import pennylane as qml

# Já disponíveis: prepare_input() prepara |ψ⟩ no qubit 0, e inject_error() aplica o
# erro escolhido nos botões (qubits de dados 0, 1 e 2). Ancillas: qubits 3 e 4.
dev = qml.device("default.mixed", wires=5)


def encode():
    # α|0⟩ + β|1⟩  ->  α|000⟩ + β|111⟩
    pass


def recover():
    # 1. Síndrome nas ancillas 3 e 4.
    # 2. Correção com Toffoli, sem medir.
    pass


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
