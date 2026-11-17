# Hidden setup for the challenge of lesson 3.1: `mystery(theta)`, a one-qubit cost with a single
# free angle and fixed gates around it. Its three coefficients are what the learner must recover.
def _build_mystery():
    import pennylane as _qml

    _dev = _qml.device("default.qubit", wires=1)

    @_qml.qnode(_dev)
    def mystery(theta):
        _qml.RY(0.9, wires=0)
        _qml.RX(theta, wires=0)
        _qml.RY(0.5, wires=0)
        _qml.RZ(0.3, wires=0)
        return _qml.expval(_qml.PauliX(0) + 0.5 * _qml.PauliZ(0))

    return mystery


mystery = _build_mystery()
del _build_mystery
