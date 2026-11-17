"""Challenge for lesson 4.6: a minimum-weight decoder on the 3x3 torus for two X errors.

The reference computes the syndrome and the class of a loop with binary vectors, and finds the
minimum weight by search, so the learner's decoder is tested against the definition. The class of
the loop error + correction does not depend on which minimum correction is chosen on this torus
(L = 3 is odd), so any correct decoder gives the same number of failures.
"""

import itertools
import random

import numpy as np

L = 3
EDGES = [(t, r, c) for t in "hv" for r in range(L) for c in range(L)]


def index(edge):
    kind, r, c = edge
    return (0 if kind == "h" else L * L) + r * L + c


def plaquette_matrix():
    rows = np.zeros((L * L, 2 * L * L), dtype=int)
    for r in range(L):
        for c in range(L):
            for edge in (("h", r, c), ("h", (r + 1) % L, c), ("v", r, c), ("v", r, (c + 1) % L)):
                rows[r * L + c, index(edge)] ^= 1
    return rows


MATRIX = plaquette_matrix()


def ref_defects(chain):
    e = np.zeros(2 * L * L, dtype=int)
    for edge in chain:
        e[index(edge)] ^= 1
    s = MATRIX @ e % 2
    return tuple((p // L, p % L) for p in range(L * L) if s[p])


def ref_class(chain):
    a = sum(1 for e in chain if e[0] == "h" and e[1] == 0) % 2
    b = sum(1 for e in chain if e[0] == "v" and e[2] == 0) % 2
    return (a, b)


def small_chains():
    """Defect set -> (minimum weight, one chain of that weight), over all chains of up to 2 edges."""
    table = {}
    for size in range(3):
        for candidate in itertools.combinations(EDGES, size):
            table.setdefault(ref_defects(candidate), (size, set(candidate)))
    return table


TABLE = small_chains()
PAIRS = list(itertools.combinations(EDGES, 2))


def ref_failure(error):
    _, best = TABLE[ref_defects(error)]
    return ref_class(set(error) ^ best) != (0, 0)


def hidden_errors():
    rng = random.Random(11)
    bad = [p for p in PAIRS if ref_failure(p)]
    good = [p for p in PAIRS if not ref_failure(p)]
    return [set(p) for p in rng.sample(bad, 4) + rng.sample(good, 8)]


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def short(chain):
    return str(sorted(chain))


def valid_chain(value):
    try:
        chain = {tuple(e) for e in value}
    except TypeError:
        return None
    for e in chain:
        if len(e) != 3 or e[0] not in ("h", "v") or not all(isinstance(x, (int, np.integer)) for x in e[1:]):
            return None
        if not (0 <= e[1] < L and 0 <= e[2] < L):
            return None
    return {(e[0], int(e[1]), int(e[2])) for e in chain}


def check(ns, run_case):
    for name in ("decode", "outcome"):
        if not callable(ns.get(name)):
            return fail("ch_missing_function", name=name)
    decode, outcome = ns["decode"], ns["outcome"]

    for error in hidden_errors():
        found = list(ref_defects(error))
        try:
            correction = valid_chain(decode(L, list(found)))
        except Exception:
            correction = None
        if correction is None:
            return fail("ch_bad_chain", found=found)
        left = ref_defects(correction)
        if left != tuple(found):
            return fail("ch_defects_left", found=found, correction=short(correction), left=list(left))
        best = TABLE[tuple(found)][0]
        if len(correction) != best:
            return fail("ch_not_minimal", found=found, size=len(correction), best=best)
        expected = "failure" if ref_failure(error) else "success"
        try:
            got = outcome(L, set(error), set(correction))
        except Exception:
            got = None
        if got != expected:
            return fail("ch_outcome_wrong", error=short(error), correction=short(correction), expected=expected, got=got)

    # outcome alone, on a correction that is not minimal: the stabilizer loop around a star is harmless,
    # a loop that wraps around the torus is not.
    error = {("h", 1, 1), ("v", 2, 2)}
    star = {("h", 0, 0), ("h", 0, 2), ("v", 0, 0), ("v", 2, 0)}
    wrap = {("v", 1, c) for c in range(L)}
    for extra, expected in ((star, "success"), (wrap, "failure")):
        try:
            got = outcome(L, set(error), set(error) ^ extra)
        except Exception:
            got = None
        if got != expected:
            return fail("ch_outcome_wrong", error=short(error), correction=short(set(error) ^ extra), expected=expected, got=got)

    total = len(PAIRS)
    want = sum(1 for p in PAIRS if ref_failure(p))
    for name, value in (("failures", want), ("total", total)):
        if name not in ns:
            return fail("ch_missing", name=name)
        try:
            actual = int(ns[name])
        except (TypeError, ValueError):
            return fail("ch_missing", name=name)
        if actual != value:
            return fail("ch_wrong_count", name=name, actual=actual)
    return {"passed": True, "key": "ch_ok", "params": {"failures": want, "total": total}}
