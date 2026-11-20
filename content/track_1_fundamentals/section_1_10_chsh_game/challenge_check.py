"""Challenge for lesson 1.10 (CHSH game with fixed Bob).

Lesson rules, plus: Bob's rotation is exactly Ry(BOB[y]).

For the four questions (x, y): the circuit has a single two-qubit gate (the
Bell pair); Alice's rotation depends only on x and Bob's only on y; the exact
winning probability, computed here from the state vector, reaches at least
0.85; and the learner's `win_probability` matches it.
"""

from math import pi

from qiskit import QuantumCircuit

from ket_lab_engine import simulator

QUESTIONS = [(0, 0), (0, 1), (1, 0), (1, 1)]
THRESHOLD = 0.85
BOB = {0: round(pi / 3, 9), 1: round(-pi / 6, 9)}  # Bob's angles, fixed


def single_qubit_gates(circuit, qubit):
    gates = []
    for item in circuit.data:
        name = item.operation.name
        if name in ("barrier", "measure") or len(item.qubits) != 1:
            continue
        if circuit.find_bit(item.qubits[0]).index == qubit:
            params = tuple(round(float(p), 9) for p in item.operation.params)
            gates.append((name, params))
    return gates


def win_probability(play):
    total = 0.0
    for x, y in QUESTIONS:
        distribution = simulator.register_distribution(play(x, y), [0, 1])  # label "b a"
        for label, p in distribution.items():
            a, b = int(label[1]), int(label[0])
            if (a ^ b) == (x & y):
                total += p / 4
    return total


def check(ns, run_case):
    play = ns.get("play")
    if not callable(play):
        return {"passed": False, "key": "no_play"}
    circuits = {}
    for question in QUESTIONS:
        circuit = play(*question)
        if not isinstance(circuit, QuantumCircuit) or circuit.num_qubits != 2:
            return {"passed": False, "key": "wrong_size"}
        two_qubit = [i for i in circuit.data if len(i.qubits) == 2 and i.operation.name != "barrier"]
        if len(two_qubit) != 1:
            return {"passed": False, "key": "gate_count", "params": {"count": len(two_qubit)}}
        circuits[question] = circuit
    for x, y in QUESTIONS:
        other_y = circuits[(x, 1 - y)]
        other_x = circuits[(1 - x, y)]
        circuit = circuits[(x, y)]
        if single_qubit_gates(circuit, 0) != single_qubit_gates(other_y, 0):
            return {"passed": False, "key": "alice_local"}
        if single_qubit_gates(circuit, 1) != single_qubit_gates(other_x, 1):
            return {"passed": False, "key": "bob_local"}
    for x, y in QUESTIONS:
        if single_qubit_gates(circuits[(x, y)], 1) != [("ry", (BOB[y],))]:
            return {"passed": False, "key": "bob_fixed"}
    exact = win_probability(play)
    if exact < THRESHOLD:
        return {"passed": False, "key": "low", "params": {"probability": exact, "threshold": THRESHOLD}}
    reported = ns.get("win_probability")
    if not isinstance(reported, (int, float)):
        return {"passed": False, "key": "variable_missing", "params": {"probability": exact}}
    if abs(float(reported) - exact) > 1e-6:
        return {"passed": False, "key": "variable_wrong", "params": {"reported": float(reported), "probability": exact}}
    return {"passed": True, "key": "ok", "params": {"probability": exact}}
