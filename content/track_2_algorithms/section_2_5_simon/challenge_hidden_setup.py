# Setup oculto do desafio da lição 2.5: oráculo compacto de Simon, n = 3 entradas e
# apenas 2 saídas (qubits 3 e 4). f(x) = (x_i ⊕ x_j s_i) para os dois índices i ≠ j, onde j
# é o menor índice com s_j = 1; f(x) = f(y) se e somente se y = x ou y = x ⊕ s. s ≠ 000.
try:
    _segredo = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _segredo = "110"


def _criar_oraculo(segredo):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(5, name="oracle")
    bits = [int(c) for c in reversed(segredo)]
    j = bits.index(1)
    for k, i in enumerate([i for i in range(3) if i != j]):
        circuito.cx(i, 3 + k)
        if bits[i]:
            circuito.cx(j, 3 + k)
    porta = circuito.to_gate()

    def oracle(qc):
        """Consulta f: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (entrada: qubits 0 a 2; saída: qubits 3 e 4)."""
        qc.append(porta, [0, 1, 2, 3, 4])

    return oracle


oracle = _criar_oraculo(_segredo)
del _criar_oraculo, _segredo
