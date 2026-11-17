# Hidden setup for lesson 2.6: phase oracle that marks a list of secret items
# and the variable num_marked (M), the number of marked items.
# The validator swaps the list (via _QLP_INPUT) to test several cases.
try:
    _marked_items = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _marked_items = ["1011"]
if isinstance(_marked_items, str):
    _marked_items = [_marked_items]

num_marked = len(_marked_items)


def _build_oracle(marked_items):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(4, name="grover_oracle")
    for marked_item in marked_items:
        zeros = [qubit for qubit, bit in enumerate(reversed(marked_item)) if bit == "0"]
        for qubit in zeros:
            circuit.x(qubit)
        circuit.h(3)
        circuit.mcx([0, 1, 2], 3)
        circuit.h(3)
        for qubit in zeros:
            circuit.x(qubit)
    gate = circuit.to_gate()

    def oracle(qc):
        """Flips the sign of each marked (secret) state."""
        qc.append(gate, [0, 1, 2, 3])

    return oracle


oracle = _build_oracle(_marked_items)
del _build_oracle, _marked_items
