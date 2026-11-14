"""Dados das visualizações da lição 3.1: paisagem do custo e trajetória do otimizador."""

import numpy as np

GRID = 41


def analyze(ns):
    circuit = ns["circuit"]
    axis = np.linspace(-np.pi, np.pi, GRID)
    a, b = np.meshgrid(axis, axis)  # linhas: θ₁; colunas: θ₀
    try:  # broadcasting do PennyLane: uma chamada para a grade inteira
        values = np.asarray(circuit(np.array([a.ravel(), b.ravel()]))).reshape(GRID, GRID)
    except Exception:  # noqa: BLE001 - circuito alterado sem suporte a broadcasting
        values = np.array([[float(circuit(np.array([x, y]))) for x in axis] for y in axis])
    history = [list(map(float, row[:3])) for row in (ns.get("history") or []) if len(row) >= 3]
    return {
        "landscape": {
            "x": axis, "y": axis, "z": values,
            "x_label": "θ₀", "y_label": "θ₁",
            "path": [[row[0], row[1]] for row in history],
            "min": -1.0, "max": 1.0,
        },
        "convergence": {"values": [row[2] for row in history], "target": -1.0, "y_label": "⟨Z⟩"},
    }
