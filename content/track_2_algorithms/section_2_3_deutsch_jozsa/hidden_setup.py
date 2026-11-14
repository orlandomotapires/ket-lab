# Setup oculto da lição 2.3: o oráculo da função secreta.
# O validador troca a função (via _QLP_INPUT) para testar vários oráculos.
try:
    _funcao = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _funcao = {"kind": "balanced", "mask": [1, 0, 1], "flip": 0}


def _criar_oraculo(funcao):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(4, name="oracle")
    if funcao["kind"] == "constant":
        if funcao["value"]:
            circuito.x(3)
    elif funcao["kind"] == "balanced":  # f(x) = mask·x ⊕ flip
        for qubit, bit in enumerate(funcao["mask"]):
            if bit:
                circuito.cx(qubit, 3)
        if funcao.get("flip"):
            circuito.x(3)
    elif funcao["kind"] == "majority":  # f(x) = maioria de x0, x1, x2: balanceada e não linear
        circuito.ccx(0, 1, 3)
        circuito.ccx(0, 2, 3)
        circuito.ccx(1, 2, 3)
    elif funcao["kind"] == "last":  # f(x) = x2: só o último qubit importa
        circuito.cx(2, 3)
    else:  # f(x) = x0 ⊕ (x1 · x2): balanceada e não linear
        circuito.cx(0, 3)
        circuito.ccx(1, 2, 3)
    porta = circuito.to_gate()

    def oracle(qc):
        """Consulta a função secreta: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (entrada 0 a 2, auxiliar 3)."""
        qc.append(porta, [0, 1, 2, 3])

    return oracle


oracle = _criar_oraculo(_funcao)
del _criar_oraculo, _funcao
