from math import pi
from qiskit import QuantumCircuit

alice_angle = {0: 0.0, 1: pi / 2}
bob_angle = {0: pi / 4, 1: -pi / 4}


def play(x, y):
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.ry(alice_angle[x], 0)
    qc.ry(bob_angle[y], 1)
    return qc


qc = play(1, 1)

win_probability = 0.0
for x in (0, 1):
    for y in (0, 1):
        for (a, b), p in outcome_probabilities(play(x, y)).items():
            if (a ^ b) == (x & y):
                win_probability += p / 4
