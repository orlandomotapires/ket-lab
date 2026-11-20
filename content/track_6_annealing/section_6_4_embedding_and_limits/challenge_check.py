"""Challenge for lesson 6.4: the smallest chain strength that works, for any triangle instance.

`min_chain_strength(h, J)` receives the fields h = [h0, h1, h2] and the couplings
J = {(0, 1): ..., (0, 2): ..., (1, 2): ...} of a logical problem, embeds it as in the mission
(chain 2–3 with coupling −F, all of h2 on qubit 2, J02 on edge 3–0) and returns the threshold in F:
the value above which every lowest-energy physical state has an intact chain (it then decodes to
a ground state of the logical problem), and 0 when the chain holds for every F > 0.

The check uses four instances of its own and computes the threshold from the energies. An intact
state has energy E_logical − F and a broken one has E_broken + F, where E_broken leaves out the
chain term, so the intact ground state wins once F > (E_ground − E_broken_min)/2 and keeps winning
for larger F. At exactly that F a broken state ties, and the tie is not counted as intact. The
answer is accepted within 0.01, so a scan with step 0.01 passes whichever way it treats the tie.
A brute-force scan over F is run once per instance as a cross-check of the formula.
"""

import itertools

TOLERANCE = 0.01
# (fields, couplings), thresholds below 2; the last one has no threshold at all.
INSTANCES = [
    ([-0.95, 0.04, 0.39], {(0, 1): 0.88, (0, 2): -1.22, (1, 2): -0.59}),
    ([-0.87, -0.32, 1.06], {(0, 1): 0.43, (0, 2): -1.2, (1, 2): 1.47}),
    ([0.57, 0.25, -1.08], {(0, 1): -1.39, (0, 2): -1.45, (1, 2): 1.23}),
    ([0.5, -0.3, 0.8], {(0, 1): 0.7, (0, 2): -0.9, (1, 2): 0.4}),
]


def _physical(h, J, s, F):
    return (h[0] * s[0] + h[1] * s[1] + h[2] * s[2]
            + J[(0, 1)] * s[0] * s[1] + J[(1, 2)] * s[1] * s[2] + J[(0, 2)] * s[0] * s[3]
            - F * s[2] * s[3])


def exact_threshold(h, J):
    states = list(itertools.product([1, -1], repeat=4))
    ground = min(_physical(h, J, s, 0.0) for s in states if s[2] == s[3])
    broken = min(_physical(h, J, s, 0.0) for s in states if s[2] != s[3])
    return max(0.0, (ground - broken) / 2)


def _intact(h, J, F):
    energies = sorted((_physical(h, J, s, F), s) for s in itertools.product([1, -1], repeat=4))
    low = energies[0][0]
    return all(s[2] == s[3] for e, s in energies if e < low + 1e-9)


def check(ns, run_case):
    function = ns.get("min_chain_strength")
    if not callable(function):
        return {"passed": False, "key": "ch_no_function"}
    for h, J in INSTANCES:
        want = exact_threshold(h, J)
        # Cross-check: the chain holds just above the threshold and not just below it.
        assert _intact(h, J, want + 1e-6) and (want == 0 or not _intact(h, J, want - 1e-6))
        try:
            got = float(function(list(h), dict(J)))
        except Exception as error:  # noqa: BLE001
            return {"passed": False, "key": "ch_error", "params": {"error": f"{type(error).__name__}: {error}"}}
        if got != got or abs(got) == float("inf"):
            return {"passed": False, "key": "ch_bad_return"}
        if abs(got - want) > TOLERANCE:
            return {"passed": False, "key": "ch_wrong", "params": {"got": round(got, 3), "want": round(want, 3), "h": h, "J": {f"{a}{b}": v for (a, b), v in J.items()}}}
    return {"passed": True, "key": "ok", "params": {"count": len(INSTANCES)}}
