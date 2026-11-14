# Setup oculto da lição 3.3: o grafo do problema e o Hamiltoniano de custo (energia de Ising).
EDGES = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]


def _criar_custo():
    import pennylane as _qml

    return _qml.Hamiltonian([1.0] * len(EDGES), [_qml.PauliZ(i) @ _qml.PauliZ(j) for i, j in EDGES])


edges = list(EDGES)
cost_h = _criar_custo()
del _criar_custo
