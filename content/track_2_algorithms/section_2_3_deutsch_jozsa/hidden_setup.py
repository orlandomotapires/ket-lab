# Hidden setup for lesson 2.3: the oracle of the secret function.
# The validator swaps the function (via _QLP_INPUT) to test several oracles.
try:
    _spec = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _spec = {"kind": "balanced", "mask": [1, 0, 1], "flip": 0}


def _build_oracle(spec):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(4, name="oracle")
    if spec["kind"] == "constant":
        if spec["value"]:
            circuit.x(3)
    elif spec["kind"] == "balanced":  # f(x) = mask·x ⊕ flip
        for qubit, bit in enumerate(spec["mask"]):
            if bit:
                circuit.cx(qubit, 3)
        if spec.get("flip"):
            circuit.x(3)
    elif spec["kind"] == "majority":  # f(x) = majority of x0, x1, x2: balanced and nonlinear
        circuit.ccx(0, 1, 3)
        circuit.ccx(0, 2, 3)
        circuit.ccx(1, 2, 3)
    elif spec["kind"] == "last":  # f(x) = x2: only the last qubit matters
        circuit.cx(2, 3)
    else:  # f(x) = x0 ⊕ (x1 · x2): balanced and nonlinear
        circuit.cx(0, 3)
        circuit.ccx(1, 2, 3)
    gate = circuit.to_gate()

    def oracle(qc):
        """Queries the secret function: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (input 0 to 2, auxiliary 3)."""
        qc.append(gate, [0, 1, 2, 3])

    return oracle


oracle = _build_oracle(_spec)
del _build_oracle, _spec
