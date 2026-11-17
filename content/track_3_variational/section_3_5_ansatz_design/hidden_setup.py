# Hidden setup for lesson 3.5: the cost H = -|Φ⁺⟩⟨Φ⁺| = -(II + XX - YY + ZZ)/4.
def _build_hamiltonian():
    import pennylane as _qml

    ops = [
        _qml.Identity(0) @ _qml.Identity(1),
        _qml.PauliX(0) @ _qml.PauliX(1),
        _qml.PauliY(0) @ _qml.PauliY(1),
        _qml.PauliZ(0) @ _qml.PauliZ(1),
    ]
    return _qml.Hamiltonian([-0.25, -0.25, 0.25, -0.25], ops)


H = _build_hamiltonian()
del _build_hamiltonian
