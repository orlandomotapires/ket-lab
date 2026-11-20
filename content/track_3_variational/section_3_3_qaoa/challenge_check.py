"""Challenge for lesson 3.3: QAOA on a ring of 8 vertices, depth one and depth two.

The learner stores angles_p1 (one row (γ, β)), angles_p2 (two rows) and the ratios they reach. The check
does not trust the reported ratios: it simulates the ring itself, with the mission's conventions
(|+⟩ on every qubit, then IsingZZ(γ) on every edge and RX(2β) on every qubit, once per layer), and
requires the ratios of the best angles up to a small margin: 0.745 for p = 1 (the optimum is 3/4) and
0.83 for p = 2 (the optimum is 5/6). Malformed or missing values map to message keys, never to errors.
"""

import numpy as np

N = 8
EDGES = [(i, (i + 1) % N) for i in range(N)]
BEST_CUT = 8  # an even ring is bipartite: the alternating coloring cuts every edge
THRESHOLDS = {1: 0.745, 2: 0.83}
REPORT_TOLERANCE = 0.005

_BITS = (np.arange(2**N)[:, None] >> np.arange(N)) & 1
_CUT = sum(_BITS[:, i] != _BITS[:, j] for i, j in EDGES)
_ZZ = sum(1 - 2 * (_BITS[:, i] != _BITS[:, j]) for i, j in EDGES)


def ratio_of(angles):
    """Approximation ratio of the p-layer QAOA state; angles has shape (p, 2) with rows (γ, β)."""
    state = np.full(2**N, 2 ** (-N / 2), dtype=complex)
    for gamma, beta in angles:
        state = state * np.exp(-0.5j * gamma * _ZZ)
        mixer = np.array([[np.cos(beta), -1j * np.sin(beta)], [-1j * np.sin(beta), np.cos(beta)]])
        state = state.reshape((2,) * N)
        for axis in range(N):
            state = np.moveaxis(np.tensordot(mixer, state, axes=([1], [axis])), 0, axis)
        state = state.reshape(-1)
    return float(np.sum(np.abs(state) ** 2 * _CUT) / BEST_CUT)


def _read(ns, name, size):
    """The array stored under `name` as a float array with `size` entries, or None."""
    if name not in ns:
        return None
    try:
        values = np.asarray(ns[name], dtype=float).reshape(-1)
    except (TypeError, ValueError):
        return None
    if values.size != size or not np.all(np.isfinite(values)):
        return None
    return values


def check(ns, run_case):
    ratios = {}
    for p in (1, 2):
        name = f"angles_p{p}"
        if name not in ns:
            return {"passed": False, "key": "ch_no_angles", "params": {"name": name}}
        values = _read(ns, name, 2 * p)
        if values is None:
            return {"passed": False, "key": "ch_bad_angles", "params": {"name": name, "size": 2 * p, "p": p}}
        ratios[p] = ratio_of(values.reshape(p, 2))
    for p in (1, 2):
        name = f"ratio_p{p}"
        if name not in ns:
            return {"passed": False, "key": "ch_no_ratio", "params": {"name": name}}
        reported = _read(ns, name, 1)
        if reported is None:
            return {"passed": False, "key": "ch_no_ratio", "params": {"name": name}}
        if abs(reported[0] - ratios[p]) > REPORT_TOLERANCE:
            return {
                "passed": False,
                "key": "ch_ratio_mismatch",
                "params": {"name": name, "reported": float(reported[0]), "actual": ratios[p], "p": p},
            }
    info = {"r1": ratios[1], "r2": ratios[2], "gain": ratios[2] - ratios[1], "t1": THRESHOLDS[1], "t2": THRESHOLDS[2]}
    if ratios[1] < THRESHOLDS[1]:
        return {"passed": False, "key": "ch_low_p1", "params": info}
    if ratios[2] < ratios[1]:
        return {"passed": False, "key": "ch_p2_below_p1", "params": info}
    if ratios[2] < THRESHOLDS[2]:
        return {"passed": False, "key": "ch_low_p2", "params": info}
    return {"passed": True, "key": "ok", "params": info}
