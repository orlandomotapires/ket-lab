# Setup oculto da lição 1.7: prepara entradas de dois qubits.
# O validador troca a entrada (via _QLP_INPUT). Estados de base sozinhos não notariam uma fase
# errada em |11⟩, por isso há também superposições com fases diferentes.
try:
    _entrada = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _entrada = "mixed"


def _criar_preparacao(entrada):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(2, name="prepare_input")
    if entrada == "plus":
        circuito.h(0)
        circuito.h(1)
    elif entrada == "mixed":
        circuito.ry(1.15, 0)
        circuito.ry(0.7, 1)
        circuito.rz(2.2, 0)
        circuito.rz(0.9, 1)
    elif entrada == "minus_plus":
        circuito.h(0)
        circuito.h(1)
        circuito.z(1)
    else:
        for qubit in range(2):
            if (entrada >> qubit) & 1:
                circuito.x(qubit)
    porta = circuito.to_gate()

    def prepare_input(qc):
        """Prepara a entrada nos qubits 0 e 1."""
        qc.append(porta, [0, 1])

    return prepare_input


prepare_input = _criar_preparacao(_entrada)
del _criar_preparacao, _entrada
