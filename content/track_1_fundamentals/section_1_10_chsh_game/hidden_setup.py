# Hidden setup for lesson 1.10: computes the exact outcome probabilities.
def _build_probabilities():
    from qiskit.quantum_info import Statevector as _Statevector

    def outcome_probabilities(circuit):
        """Exact probability of each pair (a, b): a is Alice's result (qubit 0), b is Bob's (qubit 1)."""
        p = _Statevector(circuit).probabilities()  # index = a + 2 b (qubit 0 is the least significant bit)
        return {(a, b): float(p[a + 2 * b]) for a in (0, 1) for b in (0, 1)}

    return outcome_probabilities


outcome_probabilities = _build_probabilities()
del _build_probabilities
