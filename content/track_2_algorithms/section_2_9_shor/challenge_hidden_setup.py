# Setup oculto do desafio da lição 2.9: multiplicação controlada por a^potência módulo 15,
# com a base `a` SECRETA (o aluno só recebe N). O validador troca `a` via _QLP_INPUT.
# Registrador de trabalho nos qubits 4 a 7; também expõe a QFT inversa.
N = 15
try:
    _a = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _a = 7


def _criar_multiplicacao(base):
    import numpy as _np
    from qiskit import QuantumCircuit as _QuantumCircuit
    from qiskit.circuit.library import UnitaryGate as _UnitaryGate

    def apply_controlled_mod_mult(qc, control, power):
        """Multiplica os qubits 4 a 7 pela base secreta elevada a `power`, módulo 15, controlada por `control`."""
        fator = pow(base, power, 15)
        matriz = _np.zeros((16, 16))
        for x in range(16):
            matriz[(x * fator % 15) if x < 15 else 15, x] = 1
        porta = _UnitaryGate(matriz, label=f"×a^{power}").control(1)
        porta.name = "c_mod_mult"
        qc.append(porta, [control, 4, 5, 6, 7])

    return apply_controlled_mod_mult


apply_controlled_mod_mult = _criar_multiplicacao(_a)
del _criar_multiplicacao, _a


def _criar_qft_inversa():
    from math import pi as _pi

    from qiskit import QuantumCircuit as _QuantumCircuit

    def inverse_qft(qc, qubits):
        """Aplica a QFT inversa aos qubits dados (o primeiro é o menos significativo)."""
        n = len(qubits)
        circuito = _QuantumCircuit(n, name="qft_dagger")
        for qubit in range(n // 2):
            circuito.swap(qubit, n - qubit - 1)
        for j in range(n):
            for m in range(j):
                circuito.cp(-_pi / 2 ** (j - m), m, j)
            circuito.h(j)
        qc.append(circuito.to_gate(), list(qubits))

    return inverse_qft


inverse_qft = _criar_qft_inversa()
del _criar_qft_inversa
