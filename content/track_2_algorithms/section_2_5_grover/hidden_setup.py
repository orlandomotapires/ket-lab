# Setup oculto da lição 2.5: oráculo de fase que marca uma lista de itens secretos
# e a variável num_marked (M), a quantidade de itens marcados.
# O validador troca a lista (via _QLP_INPUT) para testar vários casos.
try:
    _marcados = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _marcados = ["1011"]
if isinstance(_marcados, str):
    _marcados = [_marcados]

num_marked = len(_marcados)


def _criar_oraculo(marcados):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(4, name="grover_oracle")
    for marcado in marcados:
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
        """Inverte o sinal de cada estado marcado (secretos)."""
        qc.append(porta, [0, 1, 2, 3])

    return oracle


oracle = _criar_oraculo(_marcados)
del _criar_oraculo, _marcados
