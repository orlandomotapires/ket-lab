"""Validation for lesson 0.4: tensor product, Qiskit ordering and product-state test."""

import numpy as np

TOL = 1e-6
ZERO = np.array([1, 0])
PLUS = np.array([1, 1]) / np.sqrt(2)
I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]])
PROD = np.kron(PLUS, ZERO)
OP_Q0 = np.kron(I2, X)
OP_Q1 = np.kron(X, I2)
AFTER = OP_Q0 @ PROD
THREE = np.kron(np.kron(PLUS, PLUS), PLUS)


def _fmt(value):
    return np.array2string(np.asarray(value), precision=3, suppress_small=True, separator=", ")


def _fail(key, **params):
    return {"passed": False, "key": key, "params": {k: v if isinstance(v, str) else _fmt(v) for k, v in params.items()}}


def _get(ns, name, shape):
    if name not in ns:
        return None, {"passed": False, "key": "missing", "params": {"name": name}}
    try:
        arr = np.asarray(ns[name], dtype=complex)
        if arr.shape != shape:
            raise ValueError
    except (TypeError, ValueError):
        return None, {
            "passed": False,
            "key": "not_array",
            "params": {"name": name, "shape": str(shape), "actual": repr(ns[name])[:40]},
        }
    return arr, None


def _get_bool(ns, name):
    if name not in ns:
        return None, {"passed": False, "key": "missing", "params": {"name": name}}
    if not isinstance(ns[name], (bool, np.bool_)):
        return None, {"passed": False, "key": "not_bool", "params": {"name": name, "actual": repr(ns[name])[:40]}}
    return bool(ns[name]), None


def _close(a, b):
    return np.allclose(a, b, atol=TOL)


def check(ns, run_case):
    value, problem = _get(ns, "prod", (4,))
    if problem:
        return problem
    if not _close(value, PROD):
        if _close(value, np.kron(ZERO, PLUS)):
            return _fail("prod_reversed", actual=value)
        return _fail("prod_wrong", expected=PROD, actual=value)

    value, problem = _get(ns, "op_q0", (4, 4))
    if problem:
        return problem
    if not _close(value, OP_Q0):
        return _fail("op_q0_swapped" if _close(value, OP_Q1) else "op_q0_wrong", actual=value)

    value, problem = _get(ns, "op_q1", (4, 4))
    if problem:
        return problem
    if not _close(value, OP_Q1):
        return _fail("op_q1_swapped" if _close(value, OP_Q0) else "op_q1_wrong", actual=value)

    value, problem = _get(ns, "after", (4,))
    if problem:
        return problem
    if not _close(value, AFTER):
        return _fail("after_wrong", expected=AFTER, actual=value)

    value, problem = _get(ns, "three", (8,))
    if problem:
        return problem
    if not _close(value, THREE):
        return _fail("three_wrong", actual=value)

    flag, problem = _get_bool(ns, "s1_product")
    if problem:
        return problem
    if flag is not False:
        return _fail("s1_wrong")
    flag, problem = _get_bool(ns, "s2_product")
    if problem:
        return problem
    if flag is not True:
        return _fail("s2_wrong")

    return {"passed": True, "key": "ok", "params": {"prod": _fmt(PROD), "after": _fmt(AFTER)}}
