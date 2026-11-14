# Setup oculto da lição 2.4: oráculo f(x) = s·x ⊕ b (mod 2) com s secreta.
# O validador troca o caso (via _QLP_INPUT): uma string s, ou {"s": s, "b": b}.
# O viés b só soma uma fase global e não altera a resposta.
try:
    _caso = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _caso = "1011"
if isinstance(_caso, str):
    _caso = {"s": _caso, "b": 0}


def _criar_oraculo(segredo, vies):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(5, name="oracle")
    # O qubit 0 corresponde ao último caractere (convenção |s3 s2 s1 s0⟩).
    for qubit, bit in enumerate(reversed(segredo)):
        if bit == "1":
            circuito.cx(qubit, 4)
    if vies:
        circuito.x(4)
    porta = circuito.to_gate()

    def oracle(qc):
        """Consulta a função secreta: |x⟩|y⟩ -> |x⟩|y ⊕ s·x ⊕ b⟩ (entrada 0 a 3, auxiliar 4)."""
        qc.append(porta, [0, 1, 2, 3, 4])

    return oracle


oracle = _criar_oraculo(_caso["s"], _caso["b"])
del _criar_oraculo, _caso
