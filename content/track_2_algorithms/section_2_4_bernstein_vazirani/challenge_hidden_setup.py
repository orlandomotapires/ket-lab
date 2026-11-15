# Setup oculto do desafio da lição 2.4: oráculo de FASE (sem qubit auxiliar) para
# f(x) = s·x ⊕ b: |x⟩ -> (-1)^f(x) |x⟩, nos qubits 0 a 3.
try:
    _caso = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _caso = "1011"
if isinstance(_caso, str):
    _caso = {"s": _caso, "b": 0}


def _criar_oraculo(segredo, vies):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuito = _QuantumCircuit(4, name="phase_oracle")
    for qubit, bit in enumerate(reversed(segredo)):
        if bit == "1":
            circuito.z(qubit)
    if vies:
        circuito.global_phase = 3.141592653589793
    porta = circuito.to_gate()

    def phase_oracle(qc):
        """Aplica |x⟩ -> (-1)^(s·x ⊕ b) |x⟩ aos qubits 0 a 3 (sem auxiliar)."""
        qc.append(porta, [0, 1, 2, 3])

    return phase_oracle


phase_oracle = _criar_oraculo(_caso["s"], _caso["b"])
del _criar_oraculo, _caso
