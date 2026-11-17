# Idea: after majority-vote decoding every Pauli pattern leaves one Pauli on the logical qubit, so
# the failure probability is a sum over patterns of their probabilities. Group the 64 patterns of
# each block by their effect, combine the three blocks, and bisect for the crossover with p.
import itertools

import pennylane as qml

dev = qml.device("default.mixed", wires=9)

BLOCKS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]


def encode():
    # Phase-flip code on the leaders, then a bit-flip code in each block (lesson 4.4).
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[0, 6])
    for leader in (0, 3, 6):
        qml.Hadamard(wires=leader)
    for a, b, c in BLOCKS:
        qml.CNOT(wires=[a, b])
        qml.CNOT(wires=[a, c])


def decode():
    # Inner majority vote in each block, then the same vote on the leaders in the Hadamard basis.
    for a, b, c in BLOCKS:
        qml.CNOT(wires=[a, b])
        qml.CNOT(wires=[a, c])
        qml.Toffoli(wires=[b, c, a])
    for leader in (0, 3, 6):
        qml.Hadamard(wires=leader)
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[0, 6])
    qml.Toffoli(wires=[3, 6, 0])


@qml.qnode(dev)
def circuit():
    prepare_input()
    encode()
    inject_error()
    decode()
    return qml.density_matrix(wires=[0])


def block_effect(pattern):
    """(vote fails, Z count is odd) for the three Paulis of one block."""
    # X and Y are bit flips: two or more of them make the inner vote flip the wrong qubit.
    vote_fails = sum(c in "XY" for c in pattern) >= 2
    # Y and Z carry a phase flip, and each one moves the leader's sign: only the parity matters.
    z_odd = sum(c in "YZ" for c in pattern) % 2 == 1
    return vote_fails, z_odd


def combine(effects):
    """Logical Pauli from the three block effects."""
    # A failed block vote leaves X on its leader, which is Z in the |±⟩ basis: odd count, logical Z.
    logical_z = sum(f for f, _ in effects) % 2 == 1
    # An odd phase on at least two leaders beats the outer vote, which leaves a logical X.
    logical_x = sum(z for _, z in effects) >= 2
    # Both together make Y.
    return {(False, False): "I", (True, False): "X", (False, True): "Z", (True, True): "Y"}[(logical_x, logical_z)]


def logical_pauli(error):
    # Each block is reduced to its effect, and the three effects to one logical Pauli.
    return combine([block_effect([error[q] for q in block]) for block in BLOCKS])


def logical_failure(p):
    # Depolarizing channel on one qubit.
    probability = {"I": 1 - p, "X": p / 3, "Y": p / 3, "Z": p / 3}
    # Probability of each block effect, summed over the 64 patterns of one block.
    blocks = {}
    for pattern in itertools.product("IXYZ", repeat=3):
        weight = probability[pattern[0]] * probability[pattern[1]] * probability[pattern[2]]
        effect = block_effect(pattern)
        blocks[effect] = blocks.get(effect, 0.0) + weight
    # Add the probability of every combination of three block effects that leaves a logical error.
    total = 0.0
    for combo in itertools.product(blocks, repeat=3):
        if combine(combo) != "I":
            total += blocks[combo[0]] * blocks[combo[1]] * blocks[combo[2]]
    return total


def bare_failure(p):
    # An unprotected qubit fails whenever the channel applies X, Y or Z, with total probability p.
    return p


# p_L − p is negative just above 0 and positive after the crossover, so bisection finds the sign change.
low, high = 0.02, 0.2  # logical_failure < p at 0.02 and > p at 0.2
for _ in range(50):
    mid = (low + high) / 2
    if logical_failure(mid) < bare_failure(mid):
        low = mid
    else:
        high = mid
p_star = (low + high) / 2
