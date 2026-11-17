# Hidden setup for lesson 1.7: prepares two-qubit inputs.
# The validator swaps the input (via _QLP_INPUT). Basis states alone would not notice a wrong
# phase on |11⟩, so there are also superpositions with different phases.
try:
    _input = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _input = "mixed"


def _build_preparation(input_):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(2, name="prepare_input")
    if input_ == "plus":
        circuit.h(0)
        circuit.h(1)
    elif input_ == "mixed":
        circuit.ry(1.15, 0)
        circuit.ry(0.7, 1)
        circuit.rz(2.2, 0)
        circuit.rz(0.9, 1)
    elif input_ == "minus_plus":
        circuit.h(0)
        circuit.h(1)
        circuit.z(1)
    else:
        for qubit in range(2):
            if (input_ >> qubit) & 1:
                circuit.x(qubit)
    gate = circuit.to_gate()

    def prepare_input(qc):
        """Prepare the input on qubits 0 and 1."""
        qc.append(gate, [0, 1])

    return prepare_input


prepare_input = _build_preparation(_input)
del _build_preparation, _input
