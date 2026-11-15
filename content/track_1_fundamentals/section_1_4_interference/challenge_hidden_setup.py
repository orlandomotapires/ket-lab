# Setup oculto do desafio da lição 1.4: prepara |+i⟩ ou |−i⟩, sem dizer qual.
try:
    _entrada = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _entrada = "plusi"


def _criar_preparacao(entrada):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(1, name="prepare_unknown")
    circuito.h(0)
    circuito.s(0)
    if entrada == "minusi":
        circuito.z(0)
    porta = circuito.to_gate()

    def prepare_unknown(qc):
        """Prepara no qubit 0 o estado |+i⟩ ou |−i⟩ (desconhecido)."""
        qc.append(porta, [0])

    return prepare_unknown


prepare_unknown = _criar_preparacao(_entrada)
del _criar_preparacao, _entrada
