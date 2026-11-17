# Hidden setup for the lesson 2.5 challenge: compact Simon oracle, n = 3 inputs and
# only 2 outputs (qubits 3 and 4). f(x) = (x_i ⊕ x_j s_i) for the two indices i ≠ j, where j
# is the smallest index with s_j = 1; f(x) = f(y) if and only if y = x or y = x ⊕ s. s ≠ 000.
try:
    _secret = _QLP_INPUT
    del _QLP_INPUT
except NameError:
    _secret = "110"


def _build_oracle(secret):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(5, name="oracle")
    bits = [int(c) for c in reversed(secret)]
    j = bits.index(1)
    for k, i in enumerate([i for i in range(3) if i != j]):
        circuit.cx(i, 3 + k)
        if bits[i]:
            circuit.cx(j, 3 + k)
    gate = circuit.to_gate()

    def oracle(qc):
        """Queries f: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (input: qubits 0 to 2; output: qubits 3 and 4)."""
        qc.append(gate, [0, 1, 2, 3, 4])

    return oracle


oracle = _build_oracle(_secret)
del _build_oracle, _secret
