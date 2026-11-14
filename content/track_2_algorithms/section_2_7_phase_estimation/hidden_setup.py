# Setup oculto da lição 2.7: U = porta de fase com θ secreta, e a QFT inversa.
# O validador troca θ (via _QLP_INPUT) para testar vários operadores.
try:
    _theta = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _theta = 0.625


def _criar_potencias(theta):
    from math import pi as _pi

    from qiskit import QuantumCircuit as _QuantumCircuit

    def apply_controlled_u(qc, control, power):
        """Aplica U^power ao qubit 3, controlada pelo qubit `control`."""
        circuito = _QuantumCircuit(1, name=f"U^{power}")
        circuito.p(2 * _pi * theta * power, 0)
        porta = circuito.to_gate().control(1)
        porta.name = "c_u"
        qc.append(porta, [control, 3])

    return apply_controlled_u


apply_controlled_u = _criar_potencias(_theta)
del _criar_potencias, _theta


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
