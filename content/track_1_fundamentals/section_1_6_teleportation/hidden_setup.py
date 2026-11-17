# Hidden setup for lesson 1.6: defines the preparation of the state Alice will send.
# The validator swaps the angles (via _QLP_INPUT) to test several states.
try:
    _angles = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _angles = (1.15, 2.2)


def _build_preparation(theta, phi):
    from qiskit import QuantumCircuit as _QuantumCircuit

    # An opaque gate named "psi": the diagram shows ψ without revealing the angles.
    prep = _QuantumCircuit(1, name="psi")
    prep.ry(theta, 0)
    prep.rz(phi, 0)
    porta = prep.to_gate()

    def prepare_alice_state(qc):
        """Prepare on qubit 0 the state |ψ⟩ that Alice will teleport."""
        qc.append(porta, [0])

    return prepare_alice_state


prepare_alice_state = _build_preparation(*_angles)
del _build_preparation, _angles
