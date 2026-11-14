"""Dados das visualizações da lição 3.4: fronteira de decisão e curva de perda."""

import numpy as np

GRID = 40
LIMIT = 1.4


def analyze(ns):
    result = {}
    losses = [float(v) for v in (ns.get("history") or [])]
    if losses:
        result["convergence"] = {"values": losses, "target": 0.0, "y_label": "loss"}
    circuit, weights = ns.get("circuit"), ns.get("weights")
    if circuit is None or weights is None:
        return result
    axis = np.linspace(-LIMIT, LIMIT, GRID)
    xx, yy = np.meshgrid(axis, axis)
    grid = np.stack([xx.ravel(), yy.ravel()], axis=1)
    values = np.asarray(circuit(weights, grid), dtype=float).reshape(GRID, GRID)
    train_x = np.asarray(ns.get("X_train"))
    train_y = np.asarray(ns.get("y_train"))
    predicted = np.sign(np.asarray(circuit(weights, train_x), dtype=float))
    result["boundary"] = {
        "x": axis, "y": axis, "z": values,
        "points": [[float(p[0]), float(p[1]), float(label)] for p, label in zip(train_x, train_y)],
        "train_accuracy": float(np.mean(predicted == train_y)),
    }
    return result
