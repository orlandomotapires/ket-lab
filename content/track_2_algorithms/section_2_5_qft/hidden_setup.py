# Setup oculto da lição 2.5: prepara a entrada da QFT.
# O validador troca a entrada (via _QLP_INPUT): inteiros, |+++⟩ e uma superposição com fases.
try:
    _entrada = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _entrada = 5


def _criar_preparacao(entrada):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(3, name="prepare_input")
    if entrada == "plus":
        for qubit in range(3):
            circuito.h(qubit)
    elif entrada == "mixed":
        circuito.h(0)
        circuito.h(2)
        circuito.x(1)
        circuito.t(0)
        circuito.s(2)
    else:
        for qubit in range(3):
            if (entrada >> qubit) & 1:
                circuito.x(qubit)
    porta = circuito.to_gate()

    def prepare_input(qc):
        """Prepara a entrada |x⟩ nos qubits 0 a 2."""
        qc.append(porta, [0, 1, 2])

    return prepare_input


prepare_input = _criar_preparacao(_entrada)
del _criar_preparacao, _entrada
