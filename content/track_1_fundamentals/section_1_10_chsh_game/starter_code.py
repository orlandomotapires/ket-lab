from math import pi
from qiskit import QuantumCircuit

# Rotation Ry(angle) applied to a qubit just before it is measured in the
# computational basis. Alice's angle depends on her question bit x, Bob's on y.
alice_angle = {0: 0.0, 1: 0.0}
bob_angle = {0: 0.0, 1: 0.0}


def play(x, y):
    """Circuit for the questions x (Alice) and y (Bob). Qubit 0: Alice. Qubit 1: Bob."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)  # shared Bell pair |Φ+⟩
    # Alice rotates qubit 0 by alice_angle[x]; Bob rotates qubit 1 by bob_angle[y].
    return qc


qc = play(1, 1)  # shown in the visualizer

# outcome_probabilities(circuit) returns {(a, b): probability} for the answers a and b.
# The players win when a XOR b equals x AND y.
# Store the average winning probability over the four question pairs:
# win_probability = ...
