from qiskit import QuantumCircuit

# Idea: with only H and T, build every other gate from powers of T (T⁸ = I) and conjugation by H, then apply the sequence and its inverse.
qc = QuantumCircuit(1)
prepare_input(qc)


# X = H Z H, and Z = T⁴ is a half turn about the Z axis.
def x():
    qc.h(0)
    for _ in range(4):
        qc.t(0)  # T^4 = Z
    qc.h(0)


# S = T² is a quarter turn about Z.
def s():
    qc.t(0)
    qc.t(0)


# S† = S³ = T⁶, because T⁸ = I.
def sdg():
    for _ in range(6):
        qc.t(0)


# T† = T⁷, because T⁸ = I.
def tdg():
    for _ in range(7):
        qc.t(0)


# The sequence X, H, S, T, H applied to the input.
x(); qc.h(0); s(); qc.t(0); qc.h(0)
# Its inverse: H, T†, S†, H, X, in reverse order.
qc.h(0); tdg(); sdg(); qc.h(0); x()
