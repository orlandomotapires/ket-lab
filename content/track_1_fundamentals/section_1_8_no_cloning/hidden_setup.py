# Setup oculto da lição 1.8: prepara o estado de entrada no qubit 0.
# O validador troca os ângulos (via _QLP_INPUT) para testar várias entradas.
# O padrão é |+⟩ (theta = pi/2, phi = 0).
try:
    _angulos = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _angulos = (1.5707963267948966, 0.0)


def _criar_entrada(theta, phi):
    from qiskit import QuantumCircuit as _QuantumCircuit

    preparo = _QuantumCircuit(1, name="prepare_input")
    preparo.ry(theta, 0)
    preparo.rz(phi, 0)
    porta = preparo.to_gate()

    def prepare_input(qc):
        """Prepara no qubit 0 o estado de entrada |ψ⟩ que será copiado."""
        qc.append(porta, [0])

    return prepare_input


prepare_input = _criar_entrada(*_angulos)
del _criar_entrada, _angulos
