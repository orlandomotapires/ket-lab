# Setup oculto da lição 4.3: o estado a proteger e o erro injetado.
# A interface escolhe o erro pelos botões; o validador varia estado e erro (via _QLP_INPUT).
try:
    _config = dict(_QLP_INPUT)
    del _QLP_INPUT
except NameError:
    _config = {}


def _criar_funcoes(config):
    import pennylane as _qml

    theta, phi = config.get("input", (1.1, 0.7))
    error = config.get("error", "z1")

    def prepare_input():
        """Prepara no qubit 0 o estado |ψ⟩ que será protegido."""
        _qml.RY(theta, wires=0)
        _qml.RZ(phi, wires=0)

    def inject_error():
        """Aplica o erro escolhido nos qubits de dados (0, 1 e 2)."""
        if error in ("z0", "z1", "z2"):
            _qml.PauliZ(wires=int(error[1]))
        elif error == "z0z1":
            _qml.PauliZ(wires=0)
            _qml.PauliZ(wires=1)
        elif error == "x0":
            _qml.PauliX(wires=0)

    return prepare_input, inject_error


prepare_input, inject_error = _criar_funcoes(_config)
del _criar_funcoes, _config
