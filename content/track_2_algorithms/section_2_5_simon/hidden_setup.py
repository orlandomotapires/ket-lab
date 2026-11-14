# Setup oculto da lição 2.5: oráculo de Simon com segredo s (string de 3 bits).
# O validador troca o caso via _QLP_INPUT. Entrada: qubits 0 a 2; saída: qubits 3 a 5.
# f(x) = x ⊕ x_j s, onde j é o menor índice com s_j = 1 (f(x) = f(x ⊕ s)); com s = 000, f(x) = x.
# Uma permutação fixa da saída (X no qubit 3, SWAP dos qubits 4 e 5) esconde essa estrutura.
try:
    _segredo = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _segredo = "110"


def _criar_oraculo(segredo):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(6, name="oracle")
    bits = [int(c) for c in reversed(segredo)]  # bits[i] = s_i (qubit 0 é o último caractere)
    for i in range(3):
        circuito.cx(i, 3 + i)
    if any(bits):
        j = bits.index(1)
        for i in range(3):
            if bits[i]:
                circuito.cx(j, 3 + i)
    circuito.x(3)
    circuito.swap(4, 5)
    porta = circuito.to_gate()

    def oracle(qc):
        """Consulta f: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (entrada: qubits 0 a 2; saída: qubits 3 a 5)."""
        qc.append(porta, [0, 1, 2, 3, 4, 5])

    return oracle


oracle = _criar_oraculo(_segredo)
del _criar_oraculo, _segredo
