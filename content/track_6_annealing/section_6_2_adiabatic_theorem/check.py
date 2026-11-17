"""Validation for lesson 6.2: gap of H(s) = (1 - s) H_B + s H_P for the three-qubit
number-partitioning instance, and the success probability of an annealing sweep
for several total times.

Everything is recomputed here: the matrices, the spectrum, and a converged evolution
(midpoint rule, 2000 steps). The learner's own H_B and H_P are not used.
"""

import numpy as np

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=float)
Z = np.array([[1, 0], [0, -1]], dtype=float)


def on(op, q):
    f = [I2, I2, I2]
    f[q] = op
    return np.kron(f[2], np.kron(f[1], f[0]))


HB = -(on(X, 0) + on(X, 1) + on(X, 2))
HP = (
    on(Z, 0) / 3 + 2 * on(Z, 1) / 3 + on(Z, 2)
    + on(Z, 0) @ on(Z, 1) / 6 + on(Z, 0) @ on(Z, 2) / 4 + on(Z, 1) @ on(Z, 2) / 2
)
GRID = np.linspace(0, 1, 101)
TS = [1, 10, 100, 500]
TARGET = 6  # |110> in Qiskit's order


def spectrum(s):
    return np.linalg.eigvalsh((1 - s) * HB + s * HP)


def evolve(T, n, mid=True):
    psi = np.ones(8, dtype=complex) / np.sqrt(8)
    for k in range(n):
        s = (k + (0.5 if mid else 0.0)) / n
        w, v = np.linalg.eigh((1 - s) * HB + s * HP)
        psi = v @ (np.exp(-1j * w * T / n) * (v.conj().T @ psi))
    return psi


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def close(a, b, tol):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def check(ns, run_case):
    for name in ("gaps", "min_gap", "s_at_min", "success"):
        if name not in ns:
            return fail("missing", name=name)

    spec = [spectrum(s) for s in GRID]
    gap01 = np.array([e[1] - e[0] for e in spec])
    gap12 = np.array([e[2] - e[1] for e in spec])
    gap02 = np.array([e[2] - e[0] for e in spec])
    i_min = int(np.argmin(gap01))

    # gaps
    try:
        g = np.array([float(x) for x in ns["gaps"]])
    except (TypeError, ValueError):
        g = np.array([])
    if g.shape != gap01.shape:
        return fail("gaps_length", got=len(g), want=len(GRID))
    if not np.allclose(g, gap01, atol=1e-6):
        if np.allclose(g, gap12, atol=1e-6) or np.allclose(g, gap02, atol=1e-6):
            return fail("gaps_wrong_levels")
        return fail("gaps_wrong")

    # min_gap and s_at_min
    if not close(ns["min_gap"], gap01[i_min], 1e-6):
        return fail("min_gap_wrong", got=ns["min_gap"], want=round(float(gap01[i_min]), 4))
    if not close(ns["s_at_min"], GRID[i_min], 1e-6):
        if close(ns["s_at_min"], i_min, 1e-9):
            return fail("s_is_index", got=ns["s_at_min"])
        return fail("s_at_min_wrong", got=ns["s_at_min"], want=round(float(GRID[i_min]), 4))

    # success
    try:
        got = [float(x) for x in ns["success"]]
    except (TypeError, ValueError):
        got = []
    if len(got) != len(TS):
        return fail("success_length", got=len(got), want=len(TS))
    if any(x > 1.0 + 1e-6 or x < -1e-9 for x in got):
        return fail("not_normalized", got=max(got))

    ref = [abs(evolve(T, 2000)[TARGET]) ** 2 for T in TS]
    tol = 0.01
    if all(abs(a - b) <= tol for a, b in zip(got, ref)):
        return {
            "passed": True,
            "key": "ok",
            "params": {
                "min_gap": round(float(gap01[i_min]), 4),
                "s": round(float(GRID[i_min]), 2),
                "first": round(ref[0], 3),
                "last": round(ref[-1], 3),
            },
        }

    # Diagnose: wrong target state?
    for idx in range(8):
        if idx != TARGET:
            alt = [abs(evolve(T, 400)[idx]) ** 2 for T in TS]
            if all(abs(a - b) <= 0.02 for a, b in zip(got, alt)):
                return fail("wrong_target", label=format(idx, "03b"))

    # Too few steps: matches a coarse evolution (either rule) instead of the converged one.
    for n in (3, 5, 10, 20, 50):
        for mid in (True, False):
            coarse = [abs(evolve(T, n, mid)[TARGET]) ** 2 for T in TS]
            if all(abs(a - b) <= 0.005 for a, b in zip(got, coarse)):
                return fail("too_few_steps", n=n)

    bad = next(i for i, (a, b) in enumerate(zip(got, ref)) if abs(a - b) > tol)
    return fail("success_wrong", T=TS[bad], got=round(got[bad], 4), want=round(ref[bad], 4))
