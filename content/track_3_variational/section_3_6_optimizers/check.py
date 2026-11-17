"""Validation for lesson 3.6: final cost and number of circuit evaluations.

Does not trust the value the learner computes: recomputes -F with the final angles,
in its own simulator, and reads the evaluation counter of the cost defined by the hidden setup.
"""

import numpy as np

BUDGET = 200
TARGET = -0.97


def _ry(a):
    c, s = np.cos(a / 2), np.sin(a / 2)
    return np.array([[c, -s], [s, c]])


def _cost(p):
    cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    state = np.zeros(4)
    state[0] = 1.0
    state = np.kron(_ry(p[2]), _ry(p[3])) @ cnot @ np.kron(_ry(p[0]), _ry(p[1])) @ state
    return -float(abs(state[0] + state[3]) ** 2 / 2)


def check(ns, run_case):
    cost = ns.get("cost")
    if not hasattr(cost, "calls"):
        return {"passed": False, "key": "no_cost"}
    if "params" not in ns:
        return {"passed": False, "key": "no_params"}
    try:
        params = np.array([float(x) for x in ns["params"]])
    except (TypeError, ValueError):
        return {"passed": False, "key": "no_params"}
    if params.shape != (4,) or not np.all(np.isfinite(params)):
        return {"passed": False, "key": "no_params"}
    final = _cost(params)
    calls = int(cost.calls)
    info = {"cost": final, "calls": calls, "limit": BUDGET}
    if final > TARGET:
        return {"passed": False, "key": "not_converged", "params": info}
    if calls > BUDGET:
        return {"passed": False, "key": "over_budget", "params": info}
    energies = ns.get("energies") or []
    if not energies or abs(float(energies[-1]) - final) > 1e-6:
        return {"passed": False, "key": "energies_inconsistent", "params": info}
    return {"passed": True, "key": "ok", "params": info}
