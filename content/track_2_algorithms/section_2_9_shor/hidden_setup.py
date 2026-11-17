# Hidden setup for lesson 2.9: multiplication controlled by 7^power modulo 15
# (work register on qubits 4 to 7) and the inverse QFT.
# Also exposes the base `a` and the number to factor `N`.
a = 7
N = 15


def _build_mod_mult():
    from qiskit import QuantumCircuit as _QuantumCircuit

    def apply_controlled_mod_mult(qc, control, power):
        """Multiplies qubits 4 to 7 by 7^power modulo 15, controlled by `control`."""
        circuit = _QuantumCircuit(4, name=f"×7^{power}")
        for _ in range(power):
            # Multiplying by 7 modulo 15 is a permutation of the bits followed by NOT.
            circuit.swap(0, 1)
            circuit.swap(1, 2)
            circuit.swap(2, 3)
            for qubit in range(4):
                circuit.x(qubit)
        gate = circuit.to_gate().control(1)
        gate.name = "c_mod_mult"
        qc.append(gate, [control, 4, 5, 6, 7])

    return apply_controlled_mod_mult


apply_controlled_mod_mult = _build_mod_mult()
del _build_mod_mult


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
