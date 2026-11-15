# Setup oculto da lição 4.4: o estado a proteger e o erro injetado.
# A interface escolhe o erro pelos botões; o validador varia estado e erro (via _QLP_INPUT).
# O erro é descrito por pares letra+qubit: "y4", "x0x1", "z0z3"; "u4" é uma rotação arbitrária.
try:
    _config = dict(_QLP_INPUT)
    del _QLP_INPUT
except NameError:
    _config = {}


def _criar_funcoes(config):
    import pennylane as _qml

    theta, phi = config.get("input", (1.1, 0.7))
    error = config.get("error", "y4")
    errors = [(error[i], int(error[i + 1])) for i in range(0, len(error), 2)] if error != "none" else []

    def prepare_input():
        """Prepara no qubit 0 o estado |ψ⟩ que será protegido."""
        _qml.RY(theta, wires=0)
        _qml.RZ(phi, wires=0)

    def inject_error():
        """Aplica o erro escolhido nos nove qubits de dados."""
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


prepare_input, inject_error = _criar_funcoes(_config)
del _criar_funcoes, _config
