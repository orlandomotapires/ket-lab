# Hidden setup for the lesson 2.9 challenge: multiplication controlled by a^power modulo 15,
# with the base `a` SECRET (the learner only receives N). The validator swaps `a` via _KET_LAB_INPUT.
# Work register on qubits 4 to 7; also exposes the inverse QFT.
N = 15
try:
    _a = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    _a = 7


def _build_mod_mult(base):
    import numpy as _np
    from qiskit import QuantumCircuit as _QuantumCircuit
    from qiskit.circuit.library import UnitaryGate as _UnitaryGate

    def apply_controlled_mod_mult(qc, control, power):
        """Multiplies qubits 4 to 7 by the secret base raised to `power`, modulo 15, controlled by `control`."""
        factor = pow(base, power, 15)
        matrix = _np.zeros((16, 16))
        for x in range(16):
            matrix[(x * factor % 15) if x < 15 else 15, x] = 1
        gate = _UnitaryGate(matrix, label=f"×a^{power}").control(1)
        gate.name = "c_mod_mult"
        qc.append(gate, [control, 4, 5, 6, 7])

    return apply_controlled_mod_mult


apply_controlled_mod_mult = _build_mod_mult(_a)
del _build_mod_mult, _a


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
