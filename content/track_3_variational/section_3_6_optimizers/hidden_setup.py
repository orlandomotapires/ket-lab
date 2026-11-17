# Hidden setup for lesson 3.6: the -F cost (fidelity with |Φ⁺⟩) of a fixed 4-angle ansatz,
# wrapped in a counter that records how many times the circuit is evaluated.
def _build_cost():
    import pennylane as _qml
    from pennylane import numpy as _np

    _dev = _qml.device("default.qubit", wires=2)

    @_qml.qnode(_dev)
    def _circuit(p):
        _qml.RY(p[0], wires=0)
        _qml.RY(p[1], wires=1)
        _qml.CNOT(wires=[0, 1])
        _qml.RY(p[2], wires=0)
        _qml.RY(p[3], wires=1)
        _p00 = _qml.Projector(_np.array([1, 0, 0, 1]) / _np.sqrt(2), wires=[0, 1])
        return _qml.expval(-_p00)

    class Cost:
        """cost(params) returns -F; calls counts the evaluations."""

        def __init__(self):
            self.calls = 0

        def __call__(self, params):
            self.calls += 1
            return float(_circuit(_np.asarray(params, dtype=float)))

    return Cost()


cost = _build_cost()
del _build_cost
