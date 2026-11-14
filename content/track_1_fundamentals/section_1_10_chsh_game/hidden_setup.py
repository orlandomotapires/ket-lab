# Setup oculto da lição 1.10: calcula as probabilidades exatas dos resultados.
def _criar_probabilidades():
    from qiskit.quantum_info import Statevector as _Statevector

    def outcome_probabilities(circuit):
        """Probabilidade exata de cada par (a, b): a é o resultado de Alice (qubit 0), b o de Bob (qubit 1)."""
        p = _Statevector(circuit).probabilities()  # índice = a + 2 b (qubit 0 é o bit menos significativo)
        return {(a, b): float(p[a + 2 * b]) for a in (0, 1) for b in (0, 1)}

    return outcome_probabilities


outcome_probabilities = _criar_probabilidades()
del _criar_probabilidades
