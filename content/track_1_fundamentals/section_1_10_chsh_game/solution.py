from math import pi
from qiskit import QuantumCircuit

# Idea: choose angles so that the correlations E = cos(θ_A − θ_B) are +1/√2 for three question pairs and −1/√2 for the fourth.
# Alice measures at 0 or π/2 and Bob at ±π/4, so every pair of angles differs by π/4, except x = y = 1, where it is 3π/4.
alice_angle = {0: 0.0, 1: pi / 2}
bob_angle = {0: pi / 4, 1: -pi / 4}


def play(x, y):
    qc = QuantumCircuit(2)
    # Bell pair |Φ⁺⟩ made by a single two-qubit gate; after it the players cannot communicate.
    qc.h(0)
    qc.cx(0, 1)
    # Alice's rotation depends only on her question x, so that R_y followed by a Z measurement reads her chosen axis.
    qc.ry(alice_angle[x], 0)
    # Bob's rotation depends only on his question y.
    qc.ry(bob_angle[y], 1)
    return qc


# One circuit for the visualizer: the questions x = y = 1, the pair that must give different answers.
qc = play(1, 1)

# Average of the winning probability over the four equally likely question pairs: P_win = cos²(π/8) ≈ 0.854.
win_probability = 0.0
for x in (0, 1):
    for y in (0, 1):
        # The players win when a ⊕ b = x ∧ y; add the probability of each winning answer pair, weighted by 1/4.
        for (a, b), p in outcome_probabilities(play(x, y)).items():
            if (a ^ b) == (x & y):
                win_probability += p / 4
