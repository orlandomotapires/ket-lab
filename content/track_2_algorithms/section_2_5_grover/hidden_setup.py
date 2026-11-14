# Setup oculto da lição 2.5: oráculo de fase que marca um item secreto.
# O validador troca o item (via _QLP_INPUT) para testar vários casos.
try:
    _marcado = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _marcado = "1011"


def _criar_oraculo(marcado):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(4, name="grover_oracle")
    zeros = [qubit for qubit, bit in enumerate(reversed(marcado)) if bit == "0"]
    for qubit in zeros:
        circuito.x(qubit)
    circuito.h(3)
    circuito.mcx([0, 1, 2], 3)
    circuito.h(3)
    for qubit in zeros:
        circuito.x(qubit)
    porta = circuito.to_gate()

    def oracle(qc):
        """Inverte o sinal do estado marcado (secreto)."""
        qc.append(porta, [0, 1, 2, 3])

    return oracle


oracle = _criar_oraculo(_marcado)
del _criar_oraculo, _marcado
