# Hidden setup for lesson 2.8: U = phase gate with secret θ, and the inverse QFT.
# The validator swaps θ (via _KET_LAB_INPUT) to test several operators.
try:
    _theta = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    _theta = 0.375


def _build_powers(theta):
    from math import pi as _pi

    from qiskit import QuantumCircuit as _QuantumCircuit

    def apply_controlled_u(qc, control, power):
        """Applies U^power to qubit 3, controlled by qubit `control`."""
        circuit = _QuantumCircuit(1, name=f"U^{power}")
        circuit.p(2 * _pi * theta * power, 0)
        gate = circuit.to_gate().control(1)
        gate.name = "c_u"
        qc.append(gate, [control, 3])

    return apply_controlled_u


apply_controlled_u = _build_powers(_theta)
del _build_powers, _theta


def _build_inverse_qft():
    from math import pi as _pi

    from qiskit import QuantumCircuit as _QuantumCircuit

    def inverse_qft(qc, qubits):
        """Applies the inverse QFT to the given qubits (the first is the least significant)."""
        n = len(qubits)
        circuit = _QuantumCircuit(n, name="qft_dagger")
        for qubit in range(n // 2):
            circuit.swap(qubit, n - qubit - 1)
        for j in range(n):
            for m in range(j):
                circuit.cp(-_pi / 2 ** (j - m), m, j)
            circuit.h(j)
        qc.append(circuit.to_gate(), list(qubits))

    return inverse_qft


inverse_qft = _build_inverse_qft()
del _build_inverse_qft
