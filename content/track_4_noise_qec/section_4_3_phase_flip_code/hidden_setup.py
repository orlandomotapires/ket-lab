# Hidden setup for lesson 4.3: the state to protect and the injected error.
# The UI picks the error with its buttons; the validator varies state and error (via _QLP_INPUT).
try:
    _config = dict(_QLP_INPUT)
    del _QLP_INPUT
except NameError:
    _config = {}


def _build_functions(config):
    import pennylane as _qml

    theta, phi = config.get("input", (1.1, 0.7))
    error = config.get("error", "z1")

    def prepare_input():
        """Prepare the state |ψ⟩ to be protected on qubit 0."""
        _qml.RY(theta, wires=0)
        _qml.RZ(phi, wires=0)

    def inject_error():
        """Apply the chosen error to the data qubits (0, 1 and 2)."""
        if error in ("z0", "z1", "z2"):
            _qml.PauliZ(wires=int(error[1]))
        elif error == "z0z1":
            _qml.PauliZ(wires=0)
            _qml.PauliZ(wires=1)
        elif error == "x0":
            _qml.PauliX(wires=0)

    return prepare_input, inject_error


prepare_input, inject_error = _build_functions(_config)
del _build_functions, _config
