"""Validation for lesson 4.5: commutation of Pauli strings, syndrome and logical operators.

The reference uses matrices (Kronecker product), without the position-counting rule,
so that the learner's counting is tested against the definition.
"""

import itertools
from functools import reduce

import numpy as np

PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]]),
    "Z": np.diag([1, -1]).astype(complex),
}
BIT_FLIP = ["ZZI", "IZZ"]
FIVE_QUBIT = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]
ERRORS = ["I" * i + p + "I" * (2 - i) for i in range(3) for p in "XYZ"]
_CACHE = {}


def matrix(s):
    if s not in _CACHE:
        _CACHE[s] = reduce(np.kron, [PAULI[ch] for ch in s])
    return _CACHE[s]


def ref_commutes(a, b):
    return bool(np.allclose(matrix(a) @ matrix(b), matrix(b) @ matrix(a)))


def ref_syndrome(error, stabilizers):
    return tuple(0 if ref_commutes(error, g) else 1 for g in stabilizers)


def as_bits(value):
    return tuple(int(x) for x in value)


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def check(ns, run_case):
    for name in ("commutes", "syndrome"):
        if not callable(ns.get(name)):
            return fail("missing_function", name=name)
    commutes, syndrome = ns["commutes"], ns["syndrome"]

    for a, b in itertools.product(("".join(p) for p in itertools.product("IXYZ", repeat=3)), repeat=2):
        if bool(commutes(a, b)) != ref_commutes(a, b):
            return fail("commutes_wrong", a=a, b=b, expected=ref_commutes(a, b))

    cases = [(BIT_FLIP, e) for e in ERRORS] + [(BIT_FLIP, "XXI"), (BIT_FLIP, "ZXY")]
    cases += [(FIVE_QUBIT, "".join(p)) for p in itertools.product("IXYZ", repeat=5) if sum(c != "I" for c in p) <= 2]
    for stabilizers, error in cases:
        expected = ref_syndrome(error, stabilizers)
        try:
            got = as_bits(syndrome(error, stabilizers))
        except (TypeError, ValueError):
            got = ()
        if got != expected:
            return fail("syndrome_wrong", stabilizers=", ".join(stabilizers), error=error, expected=expected, got=got)

    table = ns.get("table")
    if not isinstance(table, dict) or not table:
        return fail("missing", name="table")
    if set(table) != set(ERRORS):
        return fail("table_keys")
    for error in ERRORS:
        expected = ref_syndrome(error, BIT_FLIP)
        try:
            got = as_bits(table[error])
        except (TypeError, ValueError):
            got = ()
        if got != expected:
            return fail("table_wrong", error=error, expected=expected, got=got)

    logical = {}
    for name in ("logical_X", "logical_Z"):
        value = ns.get(name)
        if not isinstance(value, str) or len(value) != 3 or set(value) - set("IXYZ"):
            return fail("logical_format", name=name)
        if any(not ref_commutes(value, g) for g in BIT_FLIP):
            return fail("logical_syndrome", name=name, value=value)
        # The elements of the stabilizer group (up to phase) are I, ZZI, IZZ and ZIZ.
        if value in ("III", "ZZI", "IZZ", "ZIZ"):
            return fail("logical_trivial", name=name, value=value)
        logical[name] = value
    if ref_commutes(logical["logical_X"], logical["logical_Z"]):
        return fail("logical_commute")

    undetected = sum(1 for e in ERRORS if ref_syndrome(e, BIT_FLIP) == (0, 0))
    return {"passed": True, "key": "ok", "params": {"undetected": undetected}}
