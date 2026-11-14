# Setup oculto da lição 1.6: define a preparação do estado que Alice vai enviar.
# O validador troca os ângulos (via _QLP_INPUT) para testar vários estados.
try:
    _angulos = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _angulos = (1.15, 2.2)


def _criar_preparacao(theta, phi):
    from qiskit import QuantumCircuit as _QuantumCircuit

    # Uma porta opaca chamada "psi": o diagrama mostra ψ, sem revelar os ângulos.
    preparo = _QuantumCircuit(1, name="psi")
    preparo.ry(theta, 0)
    preparo.rz(phi, 0)
    porta = preparo.to_gate()

    def prepare_alice_state(qc):
        """Prepara no qubit 0 o estado |ψ⟩ que Alice vai teletransportar."""
        qc.append(porta, [0])

    return prepare_alice_state


prepare_alice_state = _criar_preparacao(*_angulos)
del _criar_preparacao, _angulos
