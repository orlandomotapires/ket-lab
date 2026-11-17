# Hidden setup for the lesson 1.4 challenge: prepares |+i⟩ or |−i⟩, without saying which.
try:
    _input = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _input = "plusi"


def _build_preparation(input_):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(1, name="prepare_unknown")
    circuit.h(0)
    circuit.s(0)
    if input_ == "minusi":
        circuit.z(0)
    gate = circuit.to_gate()

    def prepare_unknown(qc):
        """Prepare the state |+i⟩ or |−i⟩ (unknown) on qubit 0."""
        qc.append(gate, [0])

    return prepare_unknown


prepare_unknown = _build_preparation(_input)
del _build_preparation, _input
