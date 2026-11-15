from qiskit import QuantumCircuit

qc = QuantumCircuit(1)
prepare_input(qc)


def x():
    qc.h(0)
    for _ in range(4):
        qc.t(0)  # T^4 = Z
    qc.h(0)


def s():
    qc.t(0)
    qc.t(0)


def sdg():
    for _ in range(6):
        qc.t(0)


def tdg():
    for _ in range(7):
        qc.t(0)


# X, H, S, T, H
x(); qc.h(0); s(); qc.t(0); qc.h(0)
# Undo: H, T^-1, S^-1, H, X
qc.h(0); tdg(); sdg(); qc.h(0); x()
