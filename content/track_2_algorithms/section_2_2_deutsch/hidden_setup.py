# Hidden setup for lesson 2.2: the oracle of a secret function f:{0,1} -> {0,1}.
# The case is the table [f(0), f(1)]; the validator swaps it via _QLP_INPUT.
try:
    _table = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _table = [0, 1]  # f(x) = x: balanced


def _build_oracle(table):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(2, name="oracle")
    f0, f1 = table
    if f0 == f1:  # constant
        if f0:
            circuit.x(1)
    else:  # balanced: f(x) = x or f(x) = NOT x
        circuit.cx(0, 1)
        if f0:
            circuit.x(1)
    gate = circuit.to_gate()

    def oracle(qc):
        """Queries the secret function: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (input on qubit 0, auxiliary on qubit 1)."""
        qc.append(gate, [0, 1])

    return oracle


oracle = _build_oracle(_table)
del _build_oracle, _table
