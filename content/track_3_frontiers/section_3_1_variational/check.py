"""Validação da lição 3.1: a regra de parameter-shift e o mínimo do custo."""

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
            actual = float(shift(pnp.array(point), i))
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
    steps = max(len(ns.get("history") or []) - 1, 0)
    return {"passed": True, "key": "ok", "params": {"cost": cost, "steps": steps}}
