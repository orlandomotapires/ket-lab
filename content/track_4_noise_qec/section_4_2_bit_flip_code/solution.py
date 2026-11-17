# Idea: spread α|0⟩ + β|1⟩ over three qubits, write the parities of pairs into two ancillas,
# and let Toffoli gates controlled by the ancillas undo the flip they point to.
import pennylane as qml

dev = qml.device("default.mixed", wires=5)


def encode():
    # Two CNOT gates from qubit 0 take α|0⟩ + β|1⟩ to α|000⟩ + β|111⟩ (entangling, not copying).
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[0, 2])


def recover():
    # Syndrome: ancilla 3 = parity of qubits 0 and 1, ancilla 4 = parity of 1 and 2.
    # Both terms of the code state have the same parities, so the data qubits are not disturbed.
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[1, 3])
    qml.CNOT(wires=[1, 4])
    qml.CNOT(wires=[2, 4])
    # Correction by deferred measurement: a Toffoli fires only when both ancillas are 1, so
    # X before and after turns it into a test for a pattern with a 0.
    # (a3, a4) = (1, 0) -> X on 0; (1, 1) -> X on 1; (0, 1) -> X on 2.
    qml.PauliX(wires=4)
    qml.Toffoli(wires=[3, 4, 0])
    qml.PauliX(wires=4)
    # Pattern (1, 1) needs no X on the ancillas.
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
    # The data qubits' density matrix: the ancillas are traced out, and noise leaves a mixed state.
    return qml.density_matrix(wires=[0, 1, 2])
