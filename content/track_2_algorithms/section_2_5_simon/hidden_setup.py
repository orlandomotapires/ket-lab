# Hidden setup for lesson 2.5: Simon oracle with secret s (3-bit string).
# The validator swaps the case via _KET_LAB_INPUT. Input: qubits 0 to 2; output: qubits 3 to 5.
# f(x) = x ⊕ x_j s, where j is the smallest index with s_j = 1 (f(x) = f(x ⊕ s)); with s = 000, f(x) = x.
# A fixed permutation of the output (X on qubit 3, SWAP of qubits 4 and 5) hides this structure.
try:
    _secret = _KET_LAB_INPUT
    del _KET_LAB_INPUT
except NameError:
    _secret = "110"


def _build_oracle(secret):
    from qiskit import QuantumCircuit as _QuantumCircuit

    circuit = _QuantumCircuit(6, name="oracle")
    bits = [int(c) for c in reversed(secret)]  # bits[i] = s_i (qubit 0 is the last character)
    for i in range(3):
        circuit.cx(i, 3 + i)
    if any(bits):
        j = bits.index(1)
        for i in range(3):
            if bits[i]:
                circuit.cx(j, 3 + i)
    circuit.x(3)
    circuit.swap(4, 5)
    gate = circuit.to_gate()

    def oracle(qc):
        """Queries f: |x⟩|y⟩ -> |x⟩|y ⊕ f(x)⟩ (input: qubits 0 to 2; output: qubits 3 to 5)."""
        qc.append(gate, [0, 1, 2, 3, 4, 5])

    return oracle


oracle = _build_oracle(_secret)
del _build_oracle, _secret
