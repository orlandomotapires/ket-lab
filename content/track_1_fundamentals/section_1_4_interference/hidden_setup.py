# Setup oculto da lição 1.4: prepara |+⟩ ou |−⟩, sem dizer qual.
# O validador troca a entrada (via _QLP_INPUT) para testar os dois casos.
try:
    _entrada = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _entrada = "plus"


def _criar_preparacao(entrada):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(1, name="prepare_unknown")
    circuito.h(0)
    if entrada == "minus":
        circuito.z(0)
    porta = circuito.to_gate()

    def prepare_unknown(qc):
        """Prepara no qubit 0 o estado |+⟩ ou |−⟩ (desconhecido)."""
        qc.append(porta, [0])

    return prepare_unknown


prepare_unknown = _criar_preparacao(_entrada)
del _criar_preparacao, _entrada
