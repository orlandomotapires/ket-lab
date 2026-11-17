from math import pi
from qiskit import QuantumCircuit

# Idea: with Bob's angles fixed 90° apart, place Alice's angles so that three correlations cos(θ_A − θ_B) are +1/√2 and one is −1/√2.
# For x = 0, π/12 is halfway between Bob's π/3 and −π/6 (45° from each). For x = 1, 7π/12 is 45° from π/3 and 135° from −π/6.
alice_angle = {0: pi / 12, 1: 7 * pi / 12}
bob_angle = {0: pi / 3, 1: -pi / 6}


def play(x, y):
    qc = QuantumCircuit(2)
    # Bell pair |Φ⁺⟩ made by a single two-qubit gate.
    qc.h(0)
    qc.cx(0, 1)
    # Each rotation depends only on that player's own question.
    qc.ry(alice_angle[x], 0)
    qc.ry(bob_angle[y], 1)
    return qc


# One circuit for the visualizer: the questions x = y = 1.
qc = play(1, 1)

# Exact winning probability: sum p/4 over the answer pairs with a ⊕ b = x ∧ y, for the four question pairs.
win_probability = 0.0
for x in (0, 1):
    for y in (0, 1):
        for (a, b), p in outcome_probabilities(play(x, y)).items():
            if (a ^ b) == (x & y):
                win_probability += p / 4
