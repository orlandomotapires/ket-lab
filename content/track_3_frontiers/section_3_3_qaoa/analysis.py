"""Dados das visualizações da lição 3.3: o grafo com o corte mais provável e a convergência."""

import itertools
import math

from qlp_engine import pl, simulator

EDGES = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]
N = 5


def cut_value(bits):
    return sum(bits[i] != bits[j] for i, j in EDGES)


def analyze(ns):
    best_cut = max(cut_value(b) for b in itertools.product([0, 1], repeat=N))
    result = {}
    history = [float(v) for v in (ns.get("history") or [])]
    if history:
        # energia de Ising E = Σ⟨ZZ⟩  ->  corte esperado = (arestas − E) / 2
        result["convergence"] = {
            "values": [(len(EDGES) - e) / 2 / best_cut for e in history],
            "target": 0.85,
            "y_label": "⟨corte⟩ / máx.",
        }
    if "params" in ns and pl.is_qnode(ns.get("circuit")):
        ops, lines, n = pl.trace_qnode(ns["circuit"], [ns["params"]])
        probabilities = simulator.state_probabilities(simulator.run_ops_trajectory(ops, lines, n).states[-1])
        ranked = sorted(range(len(probabilities)), key=lambda i: -probabilities[i])
        top = []
        for index in ranked[:6]:
            bits = [(index >> node) & 1 for node in range(N)]
            top.append({"bits": format(index, f"0{N}b"), "probability": float(probabilities[index]), "cut": cut_value(bits)})
        winner = [(ranked[0] >> node) & 1 for node in range(N)]
        expected = sum(p * cut_value([(i >> k) & 1 for k in range(N)]) for i, p in enumerate(probabilities))
        positions = [[math.cos(math.pi / 2 + 2 * math.pi * k / N), -math.sin(math.pi / 2 + 2 * math.pi * k / N)] for k in range(N)]
        result["graph"] = {
            "nodes": [{"id": k, "x": positions[k][0], "y": positions[k][1], "side": winner[k]} for k in range(N)],
            "edges": [{"a": i, "b": j, "cut": winner[i] != winner[j]} for i, j in EDGES],
            "best_bits": format(ranked[0], f"0{N}b"),
            "best_cut": cut_value(winner),
            "max_cut": best_cut,
            "ratio": expected / best_cut,
            "top": top,
        }
    return result
