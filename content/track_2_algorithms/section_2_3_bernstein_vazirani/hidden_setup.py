# Setup oculto da lição 2.3: oráculo f(x) = s·x mod 2 com s secreta.
# O validador troca s (via _QLP_INPUT) para testar várias strings.
try:
    _segredo = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _segredo = "1011"


def _criar_oraculo(segredo):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(5, name="oracle")
    # O qubit 0 corresponde ao último caractere (convenção |s3 s2 s1 s0⟩).
    for qubit, bit in enumerate(reversed(segredo)):
        if bit == "1":
            circuito.cx(qubit, 4)
    porta = circuito.to_gate()

    def oracle(qc):
        """Consulta a função secreta: |x⟩|y⟩ -> |x⟩|y ⊕ s·x⟩ (entrada 0 a 3, auxiliar 4)."""
        qc.append(porta, [0, 1, 2, 3, 4])

    return oracle


oracle = _criar_oraculo(_segredo)
del _criar_oraculo, _segredo
