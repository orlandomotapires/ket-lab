# Hidden setup for lesson 2.7: prepares the QFT input.
# The validator swaps the input (via _QLP_INPUT): integers, |+++⟩ and a superposition with phases.
try:
    _input_spec = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _input_spec = 5


def _build_preparation(input_spec):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(3, name="prepare_input")
    if input_spec == "plus":
        for qubit in range(3):
            circuit.h(qubit)
    elif input_spec == "mixed":
        circuit.h(0)
        circuit.h(2)
        circuit.x(1)
        circuit.t(0)
        circuit.s(2)
    else:
        for qubit in range(3):
            if (input_spec >> qubit) & 1:
                circuit.x(qubit)
    gate = circuit.to_gate()

    def prepare_input(qc):
        """Prepares the input |x⟩ on qubits 0 to 2."""
        qc.append(gate, [0, 1, 2])

    return prepare_input


prepare_input = _build_preparation(_input_spec)
del _build_preparation, _input_spec
