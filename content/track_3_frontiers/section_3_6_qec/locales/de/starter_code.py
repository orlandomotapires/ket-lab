import pennylane as qml

# Bereits verfügbar: prepare_input() bereitet |ψ⟩ auf Qubit 0 vor, und inject_error() wendet den
# mit den Schaltflächen gewählten Fehler an (Datenqubits 0, 1 und 2). Ancillas: Qubits 3 und 4.
dev = qml.device("default.mixed", wires=5)


def encode():
    # α|0⟩ + β|1⟩  ->  α|000⟩ + β|111⟩
    pass


def recover():
    # 1. Syndrom auf den Ancillas 3 und 4.
    # 2. Korrektur mit Toffoli, ohne Messung.
    pass


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover()
    return qml.density_matrix(wires=[0, 1, 2])
