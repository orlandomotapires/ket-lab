"""Validation for lesson 3.1: the parameter-shift rule and the cost minimum."""

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

POINTS = [(0.3, 1.1), (-0.7, 2.4), (2.0, -0.5)]
TARGET = -0.99


def check(ns, run_case):
    circuit = ns.get("circuit")
    shift = ns.get("parameter_shift")
    if not callable(shift):
        return {"passed": False, "key": "shift_missing"}
    for point in POINTS:
        expected = qml.grad(circuit)(pnp.array(point, requires_grad=True))
        for i in range(2):
            # The parameter-shift rule uses exactly two circuit executions.
            with qml.Tracker(circuit.device) as tracker:
                actual = float(shift(pnp.array(point), i))
            executions = tracker.totals.get("executions", 0)
            if executions != 2:
                return {"passed": False, "key": "shift_executions", "params": {"count": executions}}
            if abs(actual - float(expected[i])) > 1e-6:
                return {
                    "passed": False,
                    "key": "shift_wrong",
                    "params": {"point": f"[{point[0]}, {point[1]}]", "i": i, "expected": float(expected[i]), "actual": actual},
                }
    if "params" not in ns:
        return {"passed": False, "key": "no_params"}
    cost = float(circuit(ns["params"]))
    if cost > TARGET:
        return {"passed": False, "key": "not_converged", "params": {"cost": cost}}
    history = ns.get("history") or []
    if len(history) < 2:
        return {"passed": False, "key": "history_missing"}
    # The landscape and the convergence plot show history: it must be the real training run.
    for row in history:  # all rows: a made-up value could coincide near the minimum
        if abs(float(circuit(pnp.array(row[:2]))) - float(row[2])) > 1e-6:
            return {"passed": False, "key": "history_inconsistent"}
    if np.max(np.abs(np.array(history[-1][:2], dtype=float) - np.array(ns["params"], dtype=float))) > 1e-6:
        return {"passed": False, "key": "history_inconsistent"}
    steps = len(history) - 1
    return {"passed": True, "key": "ok", "params": {"cost": cost, "steps": steps}}
