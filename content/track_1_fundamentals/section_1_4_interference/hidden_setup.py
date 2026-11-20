# Hidden setup for lesson 1.4: prepares |+⟩ or |−⟩, without saying which.
# The validator swaps the input (via _KET_LAB_INPUT) to test both cases.
try:
    _input = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    _input = "plus"


def _build_preparation(input_):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(1, name="prepare_unknown")
    circuit.h(0)
    if input_ == "minus":
        circuit.z(0)
    gate = circuit.to_gate()

    def prepare_unknown(qc):
        """Prepare the state |+⟩ or |−⟩ (unknown) on qubit 0."""
        qc.append(gate, [0])

    return prepare_unknown


prepare_unknown = _build_preparation(_input)
del _build_preparation, _input
