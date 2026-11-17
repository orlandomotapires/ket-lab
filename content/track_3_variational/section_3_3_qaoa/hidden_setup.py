# Hidden setup for lesson 3.3: the problem graph and the cost Hamiltonian (Ising energy).
EDGES = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]


def _build_cost():
    import pennylane as _qml

    return _qml.Hamiltonian([1.0] * len(EDGES), [_qml.PauliZ(i) @ _qml.PauliZ(j) for i, j in EDGES])


edges = list(EDGES)
cost_h = _build_cost()
del _build_cost
