# Setup oculto da lição 2.7: multiplicação controlada por 7^potência módulo 15
# (registrador de trabalho nos qubits 4 a 7) e a QFT inversa.


def _criar_multiplicacao():
    from qiskit import QuantumCircuit as _QuantumCircuit

    def apply_controlled_mod_mult(qc, control, power):
        """Multiplica os qubits 4 a 7 por 7^power módulo 15, controlada por `control`."""
        circuito = _QuantumCircuit(4, name=f"×7^{power}")
        for _ in range(power):
            # Multiplicar por 7 módulo 15 é uma permutação dos bits seguida de NOT.
            circuito.swap(0, 1)
            circuito.swap(1, 2)
            circuito.swap(2, 3)
            for qubit in range(4):
                circuito.x(qubit)
        porta = circuito.to_gate().control(1)
        porta.name = "c_mod_mult"
        qc.append(porta, [control, 4, 5, 6, 7])

    return apply_controlled_mod_mult


apply_controlled_mod_mult = _criar_multiplicacao()
del _criar_multiplicacao


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
