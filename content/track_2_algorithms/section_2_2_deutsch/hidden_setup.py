# Setup oculto da lição 2.2: o oráculo de uma função secreta f:{0,1} -> {0,1}.
# O caso é a tabela [f(0), f(1)]; o validador a troca via _QLP_INPUT.
try:
    _tabela = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _tabela = [0, 1]  # f(x) = x: balanceada


def _criar_oraculo(tabela):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(2, name="oracle")
    f0, f1 = tabela
    if f0 == f1:  # constante
        if f0:
            circuito.x(1)
    else:  # balanceada: f(x) = x ou f(x) = NOT x
        circuito.cx(0, 1)
        if f0:
            circuito.x(1)
    porta = circuito.to_gate()

    def oracle(qc):
        """Consulta a função secreta: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (entrada no qubit 0, auxiliar no qubit 1)."""
        qc.append(porta, [0, 1])

    return oracle


oracle = _criar_oraculo(_tabela)
del _criar_oraculo, _tabela
