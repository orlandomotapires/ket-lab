# Hidden setup for lesson 1.3: prepares the input state, which the learner does not know.
# The validator swaps the input (via _QLP_INPUT): |0⟩, |1⟩, |+⟩, |+i⟩ and a generic state.
try:
    _input = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _input = "generic"


def _build_preparation(input_):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(1, name="prepare_input")
    if input_ == 1:
        circuit.x(0)
    elif input_ == "plus":
        circuit.h(0)
    elif input_ == "plusi":
        circuit.h(0)
        circuit.s(0)
    elif input_ == "generic":
        circuit.ry(1.15, 0)
        circuit.rz(2.2, 0)
    gate = circuit.to_gate()

    def prepare_input(qc):
        """Prepare an unknown input state on qubit 0."""
        qc.append(gate, [0])

    return prepare_input


prepare_input = _build_preparation(_input)
del _build_preparation, _input
