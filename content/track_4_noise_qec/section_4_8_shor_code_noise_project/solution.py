import itertools

import pennylane as qml

dev = qml.device("default.mixed", wires=9)

BLOCKS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]


def encode():
    qml.CNOT(wires=[0, 3])
    qml.CNOT(wires=[0, 6])
    for leader in (0, 3, 6):
        qml.Hadamard(wires=leader)
    for a, b, c in BLOCKS:
        qml.CNOT(wires=[a, b])
        qml.CNOT(wires=[a, c])


def decode():
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
    vote_fails = sum(c in "XY" for c in pattern) >= 2
    z_odd = sum(c in "YZ" for c in pattern) % 2 == 1
    return vote_fails, z_odd


def combine(effects):
    """Logical Pauli from the three block effects."""
    logical_z = sum(f for f, _ in effects) % 2 == 1
    logical_x = sum(z for _, z in effects) >= 2
    return {(False, False): "I", (True, False): "X", (False, True): "Z", (True, True): "Y"}[(logical_x, logical_z)]


def logical_pauli(error):
    return combine([block_effect([error[q] for q in block]) for block in BLOCKS])


def logical_failure(p):
    probability = {"I": 1 - p, "X": p / 3, "Y": p / 3, "Z": p / 3}
    blocks = {}
    for pattern in itertools.product("IXYZ", repeat=3):
        weight = probability[pattern[0]] * probability[pattern[1]] * probability[pattern[2]]
        effect = block_effect(pattern)
        blocks[effect] = blocks.get(effect, 0.0) + weight
    total = 0.0
    for combo in itertools.product(blocks, repeat=3):
        if combine(combo) != "I":
            total += blocks[combo[0]] * blocks[combo[1]] * blocks[combo[2]]
    return total


def bare_failure(p):
    return p


low, high = 0.02, 0.2  # logical_failure < p at 0.02 and > p at 0.2
for _ in range(50):
    mid = (low + high) / 2
    if logical_failure(mid) < bare_failure(mid):
        low = mid
    else:
        high = mid
p_star = (low + high) / 2
