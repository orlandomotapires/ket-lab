"""Challenge for lesson 3.6: the same budget of 200 evaluations, 12 angles, two optimizers.

The learner runs parameter-shift gradient descent with `cost_ps` and SPSA with `cost_spsa`, each a counted
copy of the same 12-angle cost, and stores the final angles in params_ps and params_spsa. The check
recomputes the energy at those angles with its own simulator (the energy of H = Σ Z_i Z_{i+1} + Σ X_i on
four spins, in three layers of RY with a CNOT chain), reads the two counters, and requires that neither run
exceeded 200 evaluations or went unused, that SPSA reached -4.5 or lower (the exact minimum of H is
-5.226), and that it ended at least 0.05 below parameter shift. Missing or malformed names map to keys.
"""

import numpy as np

BUDGET = 200
TARGET = -4.5
MARGIN = 0.05
MIN_CALLS = {"cost_ps": 24, "cost_spsa": 20}  # one parameter-shift step on 12 angles costs 24


def _ry(a):
    c, s = np.cos(a / 2), np.sin(a / 2)
    return np.array([[c, -s], [s, c]])


def _kron_all(mats):
    out = np.eye(1)
    for m in mats:
        out = np.kron(out, m)
    return out


def _cnot(control, target):
    m = np.zeros((16, 16))
    for b in range(16):
        bits = [(b >> (3 - k)) & 1 for k in range(4)]
        if bits[control]:
            bits[target] ^= 1
        m[sum(v << (3 - k) for k, v in enumerate(bits)), b] = 1.0
    return m


_Z, _X, _I = np.diag([1.0, -1.0]), np.array([[0.0, 1.0], [1.0, 0.0]]), np.eye(2)


def _site(m, k):
    return _kron_all([m if q == k else _I for q in range(4)])


_H = sum(_site(_Z, k) @ _site(_Z, (k + 1) % 4) for k in range(4)) + sum(_site(_X, k) for k in range(4))
_ENT = _cnot(2, 3) @ _cnot(1, 2) @ _cnot(0, 1)


def _energy(p):
    p = np.asarray(p, dtype=float).reshape(3, 4)
    state = np.zeros(16)
    state[0] = 1.0
    for layer in range(3):
        state = _ENT @ (_kron_all([_ry(a) for a in p[layer]]) @ state)
    return float(state @ _H @ state)


def _angles(ns, name):
    if name not in ns:
        return None
    try:
        values = np.array([float(v) for v in np.asarray(ns[name]).reshape(-1)])
    except (TypeError, ValueError):
        return None
    return values if values.shape == (12,) and np.all(np.isfinite(values)) else None


def check(ns, run_case):
    final, calls = {}, {}
    for counter, name in (("cost_ps", "params_ps"), ("cost_spsa", "params_spsa")):
        cost = ns.get(counter)
        if not hasattr(cost, "calls"):
            return {"passed": False, "key": "ch_no_cost", "params": {"name": counter}}
        angles = _angles(ns, name)
        if angles is None:
            return {"passed": False, "key": "ch_no_params", "params": {"name": name}}
        final[counter], calls[counter] = _energy(angles), int(cost.calls)
    for counter in ("cost_ps", "cost_spsa"):
        if calls[counter] < MIN_CALLS[counter]:
            return {
                "passed": False,
                "key": "ch_unused",
                "params": {"name": counter, "calls": calls[counter], "minimum": MIN_CALLS[counter]},
            }
        if calls[counter] > BUDGET:
            return {
                "passed": False,
                "key": "ch_over_budget",
                "params": {"name": counter, "calls": calls[counter], "limit": BUDGET},
            }
    info = {
        "ps": final["cost_ps"], "spsa": final["cost_spsa"],
        "ps_calls": calls["cost_ps"], "spsa_calls": calls["cost_spsa"],
        "target": TARGET, "limit": BUDGET,
    }
    if final["cost_spsa"] > TARGET:
        return {"passed": False, "key": "ch_spsa_not_low", "params": info}
    if final["cost_spsa"] > final["cost_ps"] - MARGIN:
        return {"passed": False, "key": "ch_ps_not_worse", "params": info}
    return {"passed": True, "key": "ok", "params": info}
