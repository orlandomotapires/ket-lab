# Hidden setup for the challenge of lesson 3.3: the mission's 5-vertex graph stays defined, and the
# 8-vertex ring is added with its cost Hamiltonian (the sum of Z_i Z_j over the ring's edges).
EDGES = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
RING = [(i, (i + 1) % 8) for i in range(8)]


def _build_costs():
    import pennylane as _qml

    graph = _qml.Hamiltonian([1.0] * len(EDGES), [_qml.PauliZ(i) @ _qml.PauliZ(j) for i, j in EDGES])
    ring = _qml.Hamiltonian([1.0] * len(RING), [_qml.PauliZ(i) @ _qml.PauliZ(j) for i, j in RING])
    return graph, ring


edges = list(EDGES)
ring_edges = list(RING)
cost_h, ring_cost_h = _build_costs()
del _build_costs
