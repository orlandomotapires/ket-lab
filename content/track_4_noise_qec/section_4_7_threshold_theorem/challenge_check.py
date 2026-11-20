"""Challenge for lesson 4.7: a code with more qubits has a lower threshold.

The learner writes f7(p) (one level of a counting model of a distance-3 code on 7 qubits, where
any two or more errors among the 7 are fatal), fixed_point(step, lo, hi) (bisection) and
levels_for(step, p, target), and stores p7_th, k7, qubits7 and k3. The check calls the functions
on inputs of its own: f7 against the binomial sum, fixed_point on three maps (including a map
the learner has not seen), levels_for on maps and starting points where it must return a number
or None, and compares the stored values with a reference computed here.
"""

import math

from scipy.optimize import brentq


def ref_f7(p):
    return sum(math.comb(7, j) * p**j * (1 - p) ** (7 - j) for j in range(2, 8))


def ref_f3(p):
    return 3 * p * p * (1 - p) + p**3


def ref_f10(p):
    return 10 * p * p


def ref_levels(step, p, target):
    k = 0
    while p > target:
        nxt = step(p)
        if nxt >= p:
            return None
        p, k = nxt, k + 1
    return k


def ref_root(step, lo, hi):
    return brentq(lambda p: step(p) - p, lo, hi, xtol=1e-14)


# (name, reference map, bracket for the fixed point)
MAPS = [("f7", ref_f7, (0.01, 0.5)), ("f3", ref_f3, (0.1, 0.9)), ("ten", ref_f10, (0.01, 0.9))]
# (reference map, p, target)
LEVEL_CASES = [
    (ref_f7, 1e-3, 1e-15),
    (ref_f3, 1e-3, 1e-15),
    (ref_f7, 0.06, 1e-6),
    (ref_f3, 0.06, 1e-15),
    (ref_f10, 0.05, 1e-9),
    (ref_f10, 0.2, 1e-6),
    (ref_f7, 1e-3, 1e-3),
]
TOLERANCE = 1e-6


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def _number(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def check(ns, run_case):
    for name in ("f7", "fixed_point", "levels_for"):
        if not callable(ns.get(name)):
            return fail("ch_missing_function", name=name)
    f7, fixed_point, levels_for = ns["f7"], ns["fixed_point"], ns["levels_for"]

    for p in (0.0, 0.001, 0.02, 0.06, 0.3, 1.0):
        try:
            got = _number(f7(p))
        except Exception:
            got = None
        if got is None or abs(got - ref_f7(p)) > 1e-9 * max(1.0, ref_f7(p)):
            return fail("ch_f7_wrong", p=p, want=ref_f7(p), got=got if got is not None else "no number")

    for name, ref, (lo, hi) in MAPS:
        want = ref_root(ref, lo, hi)
        try:
            got = _number(fixed_point(ref, lo, hi))
        except Exception:
            got = None
        if got is None or abs(got - want) > TOLERANCE:
            return fail("ch_fixed_point_wrong", lo=lo, hi=hi, want=want, got=got if got is not None else "no number")

    for ref, p, target in LEVEL_CASES:
        want = ref_levels(ref, p, target)
        try:
            got = levels_for(ref, p, target)
        except Exception:
            got = "an error"
        if got != want:
            key = "ch_levels_none" if want is None else "ch_levels_wrong"
            return fail(key, p=p, target=target, want=want, got=got)

    for name in ("p7_th", "k7", "qubits7", "k3"):
        if name not in ns:
            return fail("ch_missing", name=name)
    p_th = ref_root(ref_f7, 0.01, 0.5)
    got = _number(ns["p7_th"])
    if got is None or abs(got - p_th) > TOLERANCE:
        return fail("ch_threshold_wrong", got=got if got is not None else "no number")
    k7 = ref_levels(ref_f7, 1e-3, 1e-15)
    k3 = ref_levels(ref_f3, 1e-3, 1e-15)
    if ns["k7"] != k7 or ns["k3"] != k3:
        return fail("ch_stored_levels_wrong", k7=ns["k7"], k3=ns["k3"], want7=k7, want3=k3)
    if ns["qubits7"] != 7**k7:
        return fail("ch_qubits_wrong", got=ns["qubits7"], k=k7, want=7**k7)
    return {
        "passed": True,
        "key": "ok",
        "params": {"p_th": p_th, "k7": k7, "qubits7": 7**k7, "k3": k3, "qubits3": 3**k3},
    }
