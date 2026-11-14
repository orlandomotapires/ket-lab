"""Validação da lição 3.3: razão de aproximação do Max-Cut, medida no estado que o
circuito do aluno prepara (não no valor que ele informa)."""

import itertools

from qlp_engine import pl, simulator

EDGES = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
THRESHOLD = 0.85
ALLOWED = {"h", "rzz", "rx", "ry", "rz", "cx", "p"}


def cut_value(bits):
    return sum(bits[i] != bits[j] for i, j in EDGES)


def expected_cut(probabilities):
    total = 0.0
    for index, p in enumerate(probabilities):
        bits = [(index >> node) & 1 for node in range(5)]  # qubit k = vértice k
        total += p * cut_value(bits)
    return total


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    if "params" not in ns:
        return {"passed": False, "key": "no_params"}
    ops, lines, n = pl.trace_qnode(circuit, [ns["params"]])
    if n != 5:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    extra = sorted({op.name for op in ops} - ALLOWED)
    if extra:
        return {"passed": False, "key": "forbidden_op", "params": {"names": ", ".join(extra)}}
    probabilities = simulator.state_probabilities(simulator.run_ops_trajectory(ops, lines, n).states[-1])
    best = max(cut_value(bits) for bits in itertools.product([0, 1], repeat=5))
    ratio = expected_cut(probabilities) / best
    params = {"ratio": ratio, "threshold": THRESHOLD, "best": best}
    if ratio >= THRESHOLD:
        return {"passed": True, "key": "ok", "params": params}
    zz_layers = sum(op.name == "rzz" for op in ops) // len(EDGES)
    if not any(op.name == "rx" for op in ops):
        return {"passed": False, "key": "no_mixer", "params": params}
    if zz_layers < 2:
        return {"passed": False, "key": "p_too_small", "params": params}
    return {"passed": False, "key": "low_ratio", "params": params}
