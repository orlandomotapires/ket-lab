# Idea: undo the encoding with the same two CNOT gates. If no qubit was flipped, qubit 0 is
# already right. If qubit 0 was flipped, qubits 1 and 2 both read 1 after the decoding, and that
# is the only case where a Toffoli gate controlled by them should flip qubit 0 back.
import pennylane as qml

dev = qml.device("default.mixed", wires=5)


def encode():
    # Two CNOT gates from qubit 0 take α|0⟩ + β|1⟩ to α|000⟩ + β|111⟩ (entangling, not copying).
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])


def recover_compact():
    # The inverse of the encoding: each CNOT is its own inverse. For a flip of qubit 1 or 2,
    # qubit 0 is untouched and the flip only shows up as a 1 on that qubit.
    qml.CNOT(wires=[0, 2])
    qml.CNOT(wires=[0, 1])
    # A flip of qubit 0 turns α|0⟩ + β|1⟩ into β|0⟩ + α|1⟩ on qubit 0 and writes 11 on qubits 1
    # and 2: no other single flip does that, so this Toffoli is a majority vote on qubit 0.
    qml.Toffoli(wires=[1, 2, 0])


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    recover_compact()
    # Qubit 0 holds |ψ⟩ again; qubits 1 and 2 hold the syndrome, so the data is decoded, not in the code space.
    return qml.density_matrix(wires=[0, 1, 2])
