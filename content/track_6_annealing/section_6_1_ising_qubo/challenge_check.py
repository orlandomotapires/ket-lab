"""Challenge of lesson 6.1: weighted Max-Cut as an Ising energy and as a QUBO.

`edges` comes from challenge_hidden_setup.py. Everything is recomputed from it.
"""

import itertools

import numpy as np

N = 5
TOL = 1e-6
CONFIGS = [np.array(c) for c in itertools.product([1, -1], repeat=N)]


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def array(ns, name, shape):
    if name not in ns:
        return None, fail("missing", name=name)
    try:
        arr = np.asarray(ns[name], dtype=float)
        if arr.shape != shape:
            raise ValueError
    except (TypeError, ValueError):
        return None, fail("not_array", name=name, shape=str(shape) if shape else "a single number", actual=repr(ns[name])[:40])
    return arr, None


def check(ns, run_case):
    edges = ns["edges"]
    W = float(sum(edges.values()))
    j_ref = np.zeros((N, N))
    for (i, j), w in edges.items():
        j_ref[i, j] = w
    energy = np.array([float(s @ j_ref @ s) for s in CONFIGS])
    cut = np.array([sum(w for (i, j), w in edges.items() if s[i] != s[j]) for s in CONFIGS], dtype=float)
    best = float(cut.max())
    n_opt = int(np.sum(cut == best))

    J, problem = array(ns, "J_cut", (N, N))
    if problem:
        return problem
    if np.any(np.abs(np.tril(J)) > TOL):
        return fail("j_not_upper")
    if np.allclose(J, -j_ref, atol=TOL):
        return fail("j_sign")
    if np.allclose(J, j_ref / 2, atol=TOL) or np.allclose(J, -j_ref / 2, atol=TOL):
        return fail("j_half")
    if not np.allclose(J, j_ref, atol=TOL):
        return fail("j_wrong")

    f = ns.get("cut_from_energy")
    if not callable(f):
        return fail("missing", name="cut_from_energy")
    try:
        values = [float(f(float(e))) for e in energy[:8]]
    except Exception:  # noqa: BLE001
        return fail("relation_error")
    if not np.allclose(values, cut[:8], atol=TOL):
        k = int(np.argmax(np.abs(np.array(values) - cut[:8])))
        if np.allclose(values, (energy[:8] - W) / 2, atol=TOL) or np.allclose(values, (energy[:8] + W) / 2, atol=TOL):
            return fail("relation_sign", got=round(values[k], 4), want=float(cut[k]), E=float(energy[k]))
        return fail("relation_wrong", got=round(values[k], 4), want=float(cut[k]), E=float(energy[k]))

    Q, problem = array(ns, "Q_cut", (N, N))
    if problem:
        return problem
    off, problem = array(ns, "offset_cut", ())
    if problem:
        return problem
    if np.any(np.abs(np.tril(Q, -1)) > TOL):
        return fail("q_not_upper")
    xs = [(1 - s) // 2 for s in CONFIGS]
    qubo = np.array([float(x @ Q @ x) + float(off) for x in xs])
    if not np.allclose(qubo, energy, atol=TOL):
        diff = energy - qubo
        if np.allclose(diff, diff[0], atol=TOL):
            return fail("q_offset", diff=round(float(diff[0]), 4))
        k = int(np.argmax(np.abs(diff)))
        return fail("q_wrong", state=xs[k], got=round(qubo[k], 4), want=round(float(energy[k]), 4))

    bc, problem = array(ns, "best_cut", ())
    if problem:
        return problem
    if abs(float(bc) - best) > TOL:
        if abs(float(bc) - (W - best) ) < TOL or abs(float(bc) - float(energy.min())) < TOL:
            return fail("best_cut_energy", got=float(bc))
        return fail("best_cut_wrong", got=float(bc))

    try:
        spins = np.asarray(ns["best_spins"], dtype=float)
        if spins.shape != (N,):
            raise ValueError
    except (KeyError, TypeError, ValueError):
        return fail("not_array", name="best_spins", shape=str((N,)), actual=repr(ns.get("best_spins"))[:40])
    if np.all(np.isin(spins, [0, 1])):
        return fail("spins_bits")
    if not np.all(np.isin(spins, [-1, 1])) or abs(float(spins @ j_ref @ spins) - energy.min()) > TOL:
        return fail("spins_not_best", got=float(sum(w for (i, j), w in edges.items() if spins[i] != spins[j])), want=best)

    n = ns.get("n_optimal")
    try:
        n = int(n)
    except (TypeError, ValueError):
        return fail("missing", name="n_optimal")
    if n != n_opt:
        if 2 * n == n_opt:
            return fail("n_mirror", got=n)
        return fail("n_wrong", got=n)

    return {"passed": True, "key": "ok", "params": {"best_cut": int(best), "n_optimal": n_opt, "energy": int(energy.min()), "W": int(W)}}
