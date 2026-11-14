"""Validação da lição 1.10 (jogo CHSH).

Para as quatro perguntas (x, y): o circuito tem um único gate de dois qubits (o
par de Bell); a rotação de Alice depende só de x e a de Bob só de y; a
probabilidade exata de vitória, calculada aqui a partir do vetor de estado,
chega a pelo menos 0,85; e `win_probability` do aluno coincide com ela.
"""

from qiskit import QuantumCircuit

from qlp_engine import simulator

QUESTIONS = [(0, 0), (0, 1), (1, 0), (1, 1)]
THRESHOLD = 0.85


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
        distribution = simulator.register_distribution(play(x, y), [0, 1])  # rótulo "b a"
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
    exact = win_probability(play)
    if exact < THRESHOLD:
        return {"passed": False, "key": "low", "params": {"probability": exact, "threshold": THRESHOLD}}
    reported = ns.get("win_probability")
    if not isinstance(reported, (int, float)):
        return {"passed": False, "key": "variable_missing", "params": {"probability": exact}}
    if abs(float(reported) - exact) > 1e-6:
        return {"passed": False, "key": "variable_wrong", "params": {"reported": float(reported), "probability": exact}}
    return {"passed": True, "key": "ok", "params": {"probability": exact}}
