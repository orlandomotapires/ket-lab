"""Validation for project 6.5: a constrained choice (two of four jobs) by annealing.

Rubric, reporting the first criterion that fails:
1. Q and offset reproduce the penalized cost on all 16 choices (A = 4);
2. best_jobs and best_value are the feasible optimum;
3. A_min is the smallest candidate weight for which the feasible optimum is the unique ground state;
4. h, J and const are the Ising form of the QUBO with s = 1 - 2x;
5. success and success_big agree with a reference evolution (H_P divided by its largest coefficient);
6. jobs is the choice the anneal at the longest time most probably selects.

Everything is recomputed from the instance; the learner's numbers are only compared with it.
"""

import itertools

import numpy as np

V = [5, 4, 3, 2]
CONFLICTS = [(0, 1), (1, 2)]
B = 6.0
A_USED = 4.0
A_BIG = 20.0
PENALTIES = [0.5, 1, 1.5, 2, 2.5, 3, 4, 6]
TS = [5, 20, 80]
N = 4
TOL = 1e-6
CHOICES = list(itertools.product([0, 1], repeat=N))
BEST = (1, 0, 1, 0)
TARGET = 0b0101

I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=float)
Z = np.diag([1.0, -1.0])


def cost(x, A):
    return (
        -sum(v * xi for v, xi in zip(V, x))
        + A * (sum(x) - 2) ** 2
        + B * sum(x[i] * x[j] for i, j in CONFLICTS)
    )


def ref_qubo(A):
    Q = np.zeros((N, N))
    for i in range(N):
        Q[i, i] = -V[i] - 3 * A
        for j in range(i + 1, N):
            Q[i, j] = 2 * A
    for i, j in CONFLICTS:
        Q[i, j] += B
    return Q, 4 * A


def ref_ising(A):
    Q, off = ref_qubo(A)
    h = np.zeros(N)
    J = np.zeros((N, N))
    const = off
    for i in range(N):
        h[i] -= Q[i, i] / 2
        const += Q[i, i] / 2
        for j in range(i + 1, N):
            J[i, j] = Q[i, j] / 4
            h[i] -= Q[i, j] / 4
            h[j] -= Q[i, j] / 4
            const += Q[i, j] / 4
    return h, J, const


def on(op, q):
    f = [I2] * N
    f[q] = op
    m = f[N - 1]
    for k in range(N - 2, -1, -1):
        m = np.kron(m, f[k])
    return m


HB = -sum(on(X, i) for i in range(N))


def hp(A, rescale=True):
    h, J, _ = ref_ising(A)
    H = sum(h[i] * on(Z, i) for i in range(N))
    for i in range(N):
        for j in range(i + 1, N):
            H = H + J[i, j] * on(Z, i) @ on(Z, j)
    return H / max(np.abs(h).max(), np.abs(J).max()) if rescale else H


def evolve(H_P, T, steps=400):
    psi = np.ones(2**N, dtype=complex) / 2 ** (N / 2)
    for k in range(steps):
        s = (k + 0.5) / steps
        w, Vv = np.linalg.eigh((1 - s) * HB + s * H_P)
        psi = Vv @ (np.exp(-1j * w * T / steps) * (Vv.conj().T @ psi))
    return np.abs(psi) ** 2


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


def number_list(ns, name, length):
    if name not in ns:
        return None, fail("missing", name=name)
    try:
        arr = np.asarray([float(x) for x in ns[name]])
    except (TypeError, ValueError):
        arr = np.array([])
    if arr.shape != (length,):
        return None, fail("not_list", name=name, length=length)
    return arr, None


def job_list(value):
    try:
        return sorted(int(round(float(i))) for i in value)
    except (TypeError, ValueError):
        return None


def check(ns, run_case):
    # 1. QUBO
    Q, problem = array(ns, "Q", (N, N))
    if problem:
        return problem
    off, problem = array(ns, "offset", ())
    if problem:
        return problem
    if np.any(np.abs(np.tril(Q, -1)) > TOL):
        return fail("q_not_upper")
    values = np.array([float(np.array(x) @ Q @ np.array(x)) + float(off) for x in CHOICES])
    want = np.array([cost(x, A_USED) for x in CHOICES])
    if not np.allclose(values, want, atol=TOL):
        diff = want - values
        if np.allclose(diff, diff[0], atol=TOL):
            return fail("offset_wrong", diff=round(float(diff[0]), 4))
        # same QUBO with the count term (sum x - 2)^2 missing or with the wrong constant
        no_count = np.array([cost(x, 0.0) for x in CHOICES])
        if np.allclose(values - values[0], no_count - no_count[0], atol=TOL):
            return fail("q_no_count")
        k = int(np.argmax(np.abs(diff)))
        return fail("q_wrong", state=CHOICES[k], got=round(float(values[k]), 4), want=round(float(want[k]), 4))

    # 2. feasible optimum
    if "best_jobs" not in ns:
        return fail("missing", name="best_jobs")
    got_jobs = job_list(ns["best_jobs"]) if hasattr(ns["best_jobs"], "__iter__") else None
    if got_jobs != [0, 2]:
        free = [i for i in range(N) if (min(CHOICES, key=lambda x: cost(x, 0.0)))[i]]
        if got_jobs == free:
            return fail("best_unconstrained", jobs=free)
        return fail("best_wrong", got=str(ns["best_jobs"])[:30])
    value, problem = array(ns, "best_value", ())
    if problem:
        return problem
    if abs(float(value) - 8) > TOL:
        return fail("best_value_wrong", got=float(value), want=8)

    # 3. threshold
    a_min, problem = array(ns, "A_min", ())
    if problem:
        return problem

    def is_ground(A):
        e = sorted((cost(x, A), x) for x in CHOICES)
        return e[0][1] == BEST and e[1][0] > e[0][0] + 1e-9

    ref_a = min(A for A in PENALTIES if is_ground(A))
    if abs(float(a_min) - ref_a) > TOL:
        tie = max(A for A in PENALTIES if not is_ground(A) and A < ref_a)
        if abs(float(a_min) - tie) < TOL:
            return fail("a_min_tie", got=float(a_min), want=ref_a)
        if float(a_min) < ref_a:
            return fail("a_min_low", got=float(a_min))
        return fail("a_min_wrong", got=float(a_min), want=ref_a)

    # 4. Ising form
    h, problem = array(ns, "h", (N,))
    if problem:
        return problem
    J, problem = array(ns, "J", (N, N))
    if problem:
        return problem
    const, problem = array(ns, "const", ())
    if problem:
        return problem
    if np.any(np.abs(np.tril(J)) > TOL):
        return fail("j_not_upper")
    h_ref, J_ref, c_ref = ref_ising(A_USED)
    if not np.allclose(J, J_ref, atol=TOL):
        for factor in (2.0, 4.0):
            if np.allclose(J, J_ref * factor, atol=TOL) or np.allclose(J, J_ref / factor, atol=TOL):
                return fail("j_factor")
        return fail("j_wrong")
    if not np.allclose(h, h_ref, atol=TOL):
        if np.allclose(h, -h_ref, atol=TOL):
            return fail("h_sign")
        return fail("h_wrong")
    if abs(float(const) - c_ref) > TOL:
        return fail("const_wrong", got=float(const), want=float(c_ref))

    # 5. anneal
    success, problem = number_list(ns, "success", len(TS))
    if problem:
        return problem
    big, problem = number_list(ns, "success_big", len(TS))
    if problem:
        return problem
    if np.any(success > 1 + 1e-6) or np.any(big > 1 + 1e-6) or np.any(success < -1e-9):
        return fail("not_normalized")
    ref = np.array([evolve(hp(A_USED), T)[TARGET] for T in TS])
    ref_big = np.array([evolve(hp(A_BIG), T)[TARGET] for T in TS])
    tol = 0.01
    if not np.allclose(success, ref, atol=tol):
        raw = np.array([evolve(hp(A_USED, rescale=False), T)[TARGET] for T in TS])
        if np.allclose(success, raw, atol=tol):
            return fail("not_rescaled")
        for idx in range(2**N):
            if idx != TARGET:
                alt = [evolve(hp(A_USED), T)[idx] for T in TS]
                if np.allclose(success, alt, atol=0.02):
                    return fail("wrong_state", label=format(idx, "04b"))
        k = int(np.argmax(np.abs(success - ref)))
        return fail("success_wrong", T=TS[k], got=round(float(success[k]), 4), want=round(float(ref[k]), 4))
    if not np.allclose(big, ref_big, atol=tol):
        if np.allclose(big, ref, atol=tol):
            return fail("big_same")
        raw_big = np.array([evolve(hp(A_BIG, rescale=False), T)[TARGET] for T in TS])
        if np.allclose(big, raw_big, atol=tol):
            return fail("not_rescaled")
        k = int(np.argmax(np.abs(big - ref_big)))
        return fail("big_wrong", T=TS[k], got=round(float(big[k]), 4), want=round(float(ref_big[k]), 4))

    # 6. decoded answer
    if "jobs" not in ns:
        return fail("missing", name="jobs")
    probs = evolve(hp(A_USED), TS[-1])
    final = int(np.argmax(probs))
    want_jobs = [i for i in range(N) if (final >> i) & 1]
    got = job_list(ns["jobs"]) if hasattr(ns["jobs"], "__iter__") and not isinstance(ns["jobs"], str) else None
    if got != want_jobs:
        if isinstance(ns["jobs"], str) or (got is not None and all(isinstance(x, (int, float, np.integer)) and x in (0, 1) for x in ns["jobs"]) and len(got) == N):
            return fail("jobs_bits")
        if got is not None and got == sorted(N - 1 - i for i in want_jobs):
            return fail("jobs_reversed", got=str(got))
        return fail("jobs_wrong", got=str(ns["jobs"])[:30], want=str(want_jobs))
    return {
        "passed": True,
        "key": "ok",
        "params": {
            "a_min": ref_a,
            "small": round(float(ref[-1]), 3),
            "big": round(float(ref_big[-1]), 3),
            "jobs": str(want_jobs),
            "value": 8,
        },
    }
