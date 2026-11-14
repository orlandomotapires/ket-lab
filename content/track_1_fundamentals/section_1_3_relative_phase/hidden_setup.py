# Setup oculto da lição 1.3: prepara o estado de entrada, que o aluno não conhece.
# O validador troca a entrada (via _QLP_INPUT): |0⟩, |1⟩, |+⟩, |+i⟩ e um estado genérico.
try:
    _entrada = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _entrada = "generic"


def _criar_preparacao(entrada):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(1, name="prepare_input")
    if entrada == 1:
        circuito.x(0)
    elif entrada == "plus":
        circuito.h(0)
    elif entrada == "plusi":
        circuito.h(0)
        circuito.s(0)
    elif entrada == "generic":
        circuito.ry(1.15, 0)
        circuito.rz(2.2, 0)
    porta = circuito.to_gate()

    def prepare_input(qc):
        """Prepara no qubit 0 um estado de entrada desconhecido."""
        qc.append(porta, [0])

    return prepare_input


prepare_input = _criar_preparacao(_entrada)
del _criar_preparacao, _entrada
