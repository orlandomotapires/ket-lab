# Hidden setup for lesson 2.4: oracle f(x) = s·x ⊕ b (mod 2) with secret s.
# The validator swaps the case (via _KET_LAB_INPUT): a string s, or {"s": s, "b": b}.
# The bias b only adds a global phase and does not change the answer.
try:
    _case = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    _case = "1011"
if isinstance(_case, str):
    _case = {"s": _case, "b": 0}


def _build_oracle(secret, bias):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(5, name="oracle")
    # Qubit 0 corresponds to the last character (convention |s3 s2 s1 s0⟩).
    for qubit, bit in enumerate(reversed(secret)):
        if bit == "1":
            circuit.cx(qubit, 4)
    if bias:
        circuit.x(4)
    gate = circuit.to_gate()

    def oracle(qc):
        """Queries the secret function: |x⟩|y⟩ -> |x⟩|y ⊕ s·x ⊕ b⟩ (input 0 to 3, auxiliary 4)."""
        qc.append(gate, [0, 1, 2, 3, 4])

    return oracle


oracle = _build_oracle(_case["s"], _case["b"])
del _build_oracle, _case
