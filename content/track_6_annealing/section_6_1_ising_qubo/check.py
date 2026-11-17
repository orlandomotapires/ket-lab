"""Validation for lesson 6.1: number partitioning as an Ising energy, brute force and the QUBO form.

Everything is recomputed from the numbers of the set; the learner's values are only compared with it.
"""

import itertools

import numpy as np

A = np.array([4, 5, 6, 7, 8])
N = len(A)
TOL = 1e-6
CONFIGS = [np.array(c) for c in itertools.product([1, -1], repeat=N)]
ENERGIES = np.array([float((A @ s) ** 2) for s in CONFIGS])
CONST = float(np.sum(A**2))
J_REF = np.array([[2.0 * A[i] * A[j] if j > i else 0.0 for j in range(N)] for i in range(N)])


def _fmt(value):
    if isinstance(value, str):
        return value
    arr = np.asarray(value)
    if arr.ndim == 0:
        return str(round(float(arr), 4))
    return np.array2string(arr, precision=3, suppress_small=True, separator=", ")


def fail(key, **params):
    return {"passed": False, "key": key, "params": {k: _fmt(v) for k, v in params.items()}}


def _get(ns, name, shape=()):
    if name not in ns:
        return None, {"passed": False, "key": "missing", "params": {"name": name}}
    try:
        arr = np.asarray(ns[name], dtype=float)
        if arr.shape != shape:
            raise ValueError
    except (TypeError, ValueError):
        return None, {
            "passed": False,
            "key": "not_array",
            "params": {"name": name, "shape": str(shape) if shape else "(a single number)", "actual": repr(ns[name])[:40]},
        }
    return arr, None


def _below(m):
    """Positions on or below the diagonal where m is not zero."""
    pos = [f"({i}, {j})" for i in range(N) for j in range(i + 1) if abs(m[i, j]) > TOL]
    return ", ".join(pos[:4]) + (", ..." if len(pos) > 4 else "")


def check(ns, run_case):
    # J
    J, problem = _get(ns, "J", (N, N))
    if problem:
        return problem
    if np.any(np.abs(np.tril(J)) > TOL):
        return fail("j_not_upper", where=_below(J))
    if np.allclose(J, J_REF / 2, atol=TOL):
        return fail("j_factor", got=J[0, 1], want=J_REF[0, 1])
    for i in range(N):
        for j in range(i + 1, N):
            if abs(J[i, j] - J_REF[i, j]) > TOL:
                return fail("j_wrong", i=str(i), j=str(j), got=J[i, j], want=J_REF[i, j])

    # energies
    en, problem = _get(ns, "energies", (len(CONFIGS),))
    if problem:
        # a list of the wrong length gets a clearer message than "not an array"
        if "energies" in ns:
            try:
                return fail("energies_shape", actual=str(np.asarray(ns["energies"], dtype=float).shape))
            except (TypeError, ValueError):
                pass
        return problem
    if not np.allclose(en, ENERGIES, atol=TOL):
        diff = ENERGIES - en
        if np.allclose(diff, diff[0], atol=TOL):
            return fail("energies_constant", diff=diff[0], const=CONST)
        if np.allclose(np.sort(en), np.sort(ENERGIES), atol=TOL):
            return fail("energies_order", first=ENERGIES[0])
        k = int(np.argmax(np.abs(en - ENERGIES)))
        return fail("energies_wrong", index=str(k), got=en[k], want=ENERGIES[k], state=CONFIGS[k])

    # ground state
    ge, problem = _get(ns, "ground_energy")
    if problem:
        return problem
    want_e = float(ENERGIES.min())
    if abs(float(ge) - want_e) > TOL:
        return fail("ground_energy_wrong", got=ge, want=want_e)
    want_states = [s for s, e in zip(CONFIGS, ENERGIES) if abs(e - want_e) < TOL]
    if "ground_states" not in ns:
        return fail("missing", name="ground_states")
    try:
        gs = np.atleast_2d(np.asarray(ns["ground_states"], dtype=float))
    except (TypeError, ValueError):
        return fail("not_array", name="ground_states", shape=f"({len(want_states)}, {N})", actual=repr(ns["ground_states"])[:40])
    if gs.ndim == 2 and gs.shape[1] == N and np.all(np.isin(gs, [0, 1])):
        return fail("ground_bits")
    got_rows = sorted(tuple(int(round(v)) for v in row) for row in gs) if gs.ndim == 2 and gs.shape[1] == N else None
    if got_rows != sorted(tuple(int(v) for v in s) for s in want_states):
        return fail("ground_wrong", n=str(len(want_states)))

    # QUBO
    Q, problem = _get(ns, "Q", (N, N))
    if problem:
        return problem
    off, problem = _get(ns, "offset")
    if problem:
        return problem
    if np.any(np.abs(np.tril(Q, -1)) > TOL):
        pos = [f"({i}, {j})" for i in range(N) for j in range(i) if abs(Q[i, j]) > TOL]
        return fail("q_not_upper", where=", ".join(pos[:4]) + (", ..." if len(pos) > 4 else ""))
    xs = [(1 - s) // 2 for s in CONFIGS]
    qubo = np.array([float(x @ Q @ x) + float(off) for x in xs])
    if not np.allclose(qubo, ENERGIES, atol=TOL):
        diff = ENERGIES - qubo
        if np.allclose(diff, diff[0], atol=TOL):
            return fail("offset_wrong", diff=diff[0])
        k = int(np.argmax(np.abs(diff)))
        upper_ok = all(abs(Q[i, j] - 8.0 * A[i] * A[j]) < TOL for i in range(N) for j in range(i + 1, N))
        key = "q_diagonal" if upper_ok else "q_wrong"
        return fail(key, state=xs[k], spins=CONFIGS[k], got=qubo[k], want=ENERGIES[k])

    return {
        "passed": True,
        "key": "ok",
        "params": {"ground_energy": int(want_e), "n_ground": len(want_states), "offset": _fmt(off)},
    }
