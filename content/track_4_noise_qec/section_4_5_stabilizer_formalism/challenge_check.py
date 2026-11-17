"""Challenge for lesson 4.5: the Steane [[7,1,3]] code from the Hamming parity-check matrix.

The reference uses binary (symplectic) vectors and a search over all 4^7 Pauli strings, so the
learner's generators, decoder and minimum logical weight are tested against the definition.
"""

import itertools

import numpy as np

HAMMING = [
    [0, 0, 0, 1, 1, 1, 1],
    [0, 1, 1, 0, 0, 1, 1],
    [1, 0, 1, 0, 1, 0, 1],
]
OTHERS = {
    "repetition": ([[1, 1, 1, 1]], True),
    "overlap_of_three": ([[1, 1, 1, 0]], False),
    "odd_overlap": ([[1, 1, 0, 0], [0, 1, 1, 0]], False),
    "two_rows": ([[1, 1, 1, 1, 0, 0], [0, 0, 1, 1, 1, 1]], True),
}


def ref_generators(H):
    return ["".join("X" if b else "I" for b in row) for row in H] + ["".join("Z" if b else "I" for b in row) for row in H]


def bits(s):
    """Binary vectors (x part, z part) of a Pauli string, up to phase."""
    return (np.array([ch in "XY" for ch in s], dtype=int), np.array([ch in "ZY" for ch in s], dtype=int))


def anticommute(a, b):
    (ax, az), (bx, bz) = bits(a), bits(b)
    return int(ax @ bz + az @ bx) % 2


def ref_valid(H):
    gens = ref_generators(H)
    return all(anticommute(a, b) == 0 for a, b in itertools.combinations(gens, 2))


def in_group(s, gens):
    """True when s equals a product of the generators, up to phase (rank test over GF(2))."""
    def vec(p):
        x, z = bits(p)
        return np.concatenate([x, z])

    def rank(rows):
        m = [r.copy() for r in rows]
        r = 0
        for col in range(len(m[0])):
            pivot = next((i for i in range(r, len(m)) if m[i][col]), None)
            if pivot is None:
                continue
            m[r], m[pivot] = m[pivot], m[r]
            for i in range(len(m)):
                if i != r and m[i][col]:
                    m[i] = (m[i] + m[r]) % 2
            r += 1
        return r

    base = [vec(g) for g in gens]
    return rank(base + [vec(s)]) == rank(base)


STEANE = ref_generators(HAMMING)
ERRORS = [("I" * i + p + "I" * (6 - i), i, p) for i in range(7) for p in "XYZ"]
MIN_WEIGHT = 3


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def check(ns, run_case):
    for name in ("css_generators", "css_valid", "locate"):
        if not callable(ns.get(name)):
            return fail("ch_missing_function", name=name)
    css_generators, css_valid, locate = ns["css_generators"], ns["css_valid"], ns["locate"]

    for H in [HAMMING] + [rows for rows, _ in OTHERS.values()]:
        want = ref_generators(H)
        try:
            got = [str(g) for g in css_generators([list(r) for r in H])]
        except Exception:
            got = []
        if got != want:
            return fail("ch_generators_wrong", H=str(H), expected=", ".join(want), got=", ".join(got) or "nothing")

    for H, expected in [(HAMMING, True)] + list(OTHERS.values()):
        try:
            got = css_valid([list(r) for r in H])
        except Exception:
            got = None
        if got is not True and got is not False and got not in (0, 1):
            return fail("ch_valid_wrong", H=str(H), expected=expected)
        if bool(got) != expected:
            return fail("ch_valid_wrong", H=str(H), expected=expected)

    for error, position, pauli in ERRORS:
        syn = tuple(anticommute(error, g) for g in STEANE)
        try:
            got = locate(syn)
            got = (int(got[0]), str(got[1]))
        except Exception:
            got = None
        if got != (position, pauli):
            return fail("ch_locate_wrong", syndrome=str(syn), expected=f"({position}, '{pauli}')", got=str(got))

    value = ns.get("min_logical")
    if not isinstance(value, str) or len(value) != 7 or set(value) - set("IXYZ"):
        return fail("ch_logical_format")
    if any(anticommute(value, g) for g in STEANE):
        return fail("ch_logical_detected", value=value)
    if in_group(value, STEANE):
        return fail("ch_logical_trivial", value=value)
    weight = sum(ch != "I" for ch in value)
    if weight != MIN_WEIGHT:
        return fail("ch_logical_heavy", value=value, weight=weight)
    # Whatever the search found, distance must agree with a full search (4^7 strings) done here.
    best = min(sum(ch != "I" for ch in "".join(p)) for p in itertools.product("IXYZ", repeat=7)
               if any(ch != "I" for ch in p) and not any(anticommute("".join(p), g) for g in STEANE)
               and not in_group("".join(p), STEANE))
    if ns.get("distance") != best:
        return fail("ch_distance_wrong", got=str(ns.get("distance")))
    return {"passed": True, "key": "ch_ok", "params": {"distance": best}}
