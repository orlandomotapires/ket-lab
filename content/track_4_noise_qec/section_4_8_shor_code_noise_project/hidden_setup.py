# Hidden setup for lesson 4.4: the state to protect and the injected error.
# The UI picks the error with its buttons; the validator varies state and error (via _QLP_INPUT).
# The error is described by letter+qubit pairs: "y4", "x0x1", "z0z3"; "u4" is an arbitrary rotation.
try:
    _config = dict(_QLP_INPUT)
    del _QLP_INPUT
except NameError:
    _config = {}


def _build_functions(config):
    import pennylane as _qml

    theta, phi = config.get("input", (1.1, 0.7))
    error = config.get("error", "y4")
    errors = [(error[i], int(error[i + 1])) for i in range(0, len(error), 2)] if error != "none" else []

    def prepare_input():
        """Prepare the state |ψ⟩ to be protected on qubit 0."""
        _qml.RY(theta, wires=0)
        _qml.RZ(phi, wires=0)

    def inject_error():
        """Apply the chosen error to the nine data qubits."""
        for kind, wire in errors:
            if kind == "x":
                _qml.PauliX(wires=wire)
            elif kind == "y":
                _qml.PauliY(wires=wire)
            elif kind == "z":
                _qml.PauliZ(wires=wire)
            else:
                _qml.RY(1.3, wires=wire)
                _qml.RX(0.6, wires=wire)
                _qml.RZ(0.9, wires=wire)

    return prepare_input, inject_error


prepare_input, inject_error = _build_functions(_config)
del _build_functions, _config
