# Hidden setup for the lesson 2.4 challenge: PHASE oracle (no auxiliary qubit) for
# f(x) = s·x ⊕ b: |x⟩ -> (-1)^f(x) |x⟩, on qubits 0 to 3.
try:
    _case = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    _case = "1011"
if isinstance(_case, str):
    _case = {"s": _case, "b": 0}


def _build_oracle(secret, bias):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(4, name="phase_oracle")
    for qubit, bit in enumerate(reversed(secret)):
        if bit == "1":
            circuit.z(qubit)
    if bias:
        circuit.global_phase = 3.141592653589793
    gate = circuit.to_gate()

    def phase_oracle(qc):
        """Applies |x⟩ -> (-1)^(s·x ⊕ b) |x⟩ to qubits 0 to 3 (no auxiliary)."""
        qc.append(gate, [0, 1, 2, 3])

    return phase_oracle


phase_oracle = _build_oracle(_case["s"], _case["b"])
del _build_oracle, _case
