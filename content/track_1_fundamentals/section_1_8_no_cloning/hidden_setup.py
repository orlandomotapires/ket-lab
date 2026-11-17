# Hidden setup for lesson 1.8: prepares the input state on qubit 0.
# The validator swaps the angles (via _QLP_INPUT) to test several inputs.
# The default is |+⟩ (theta = pi/2, phi = 0).
try:
    _angles = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _angles = (1.5707963267948966, 0.0)


def _build_input(theta, phi):
    from qiskit import QuantumCircuit as _QuantumCircuit

    prep = _QuantumCircuit(1, name="prepare_input")
    prep.ry(theta, 0)
    prep.rz(phi, 0)
    porta = prep.to_gate()

    def prepare_input(qc):
        """Prepare on qubit 0 the input state |ψ⟩ that will be copied."""
        qc.append(porta, [0])

    return prepare_input


prepare_input = _build_input(*_angles)
del _build_input, _angles
