"""Data for the lesson 3.5 visualizations: cost convergence and landscape over the first two parameters."""

import numpy as np

GRID = 41


def _landscape(ns):
    circuit = ns.get("circuit")
    params = ns.get("params")
    if circuit is None or params is None:
        return None
    base = np.array([float(p) for p in params])
    if len(base) < 2:
        return None
    axis = np.linspace(-np.pi, np.pi, GRID)
    a, b = np.meshgrid(axis, axis)  # rows: θ₁; columns: θ₀
    batch = np.tile(base[:, None], (1, GRID * GRID))
    batch[0], batch[1] = a.ravel(), b.ravel()
    try:  # PennyLane broadcasting: one call for the whole grid
        values = np.asarray(circuit(batch)).reshape(GRID, GRID)
    except Exception:  # noqa: BLE001 - circuit without broadcasting support
        values = np.zeros((GRID, GRID))
        for j, y in enumerate(axis):
            for i, x in enumerate(axis):
                point = base.copy()
                point[0], point[1] = x, y
                values[j, i] = float(circuit(point))
    return {
        "x": axis, "y": axis, "z": values,
        "x_label": "θ₀", "y_label": "θ₁",
        "path": [], "min": float(values.min()), "max": float(values.max()),
    }


def analyze(ns):
    energies = [float(e) for e in (ns.get("energies") or [])]
    result = {"convergence": {"values": energies, "target": -1.0, "band": 0.01, "y_label": "⟨H⟩"}}
    try:
        landscape = _landscape(ns)
    except Exception:  # noqa: BLE001 - modified circuit: the landscape is optional
        landscape = None
    if landscape:
        result["landscape"] = landscape
    return result
