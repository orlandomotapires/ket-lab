"""Validação da lição 0.2: norma, produto interno com conjugação, base ±."""

import numpy as np

TOL = 1e-6
V = np.array([1 + 1j, 1 - 1j])
A = np.array([1, 1j]) / np.sqrt(2)
B = np.array([1, 1]) / np.sqrt(2)
PLUS = np.array([1, 1]) / np.sqrt(2)
MINUS = np.array([1, -1]) / np.sqrt(2)
PSI = np.array([0.6, 0.8j])
PHI_PLUS = np.array([1, 0, 0, 1]) / np.sqrt(2)
Q = np.array([1, 1, 1, 1]) / 2


def _fmt(value):
    return np.array2string(np.asarray(value), precision=3, suppress_small=True, separator=", ")


def _get(ns, name, shape=()):
    """Devolve (array complexo, None) ou (None, resultado de falha)."""
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
            "params": {"name": name, "shape": str(shape) if shape else "(a single number)", "actual": repr(ns[name])[:40]},
        }
    return arr, None


def _fail(key, **params):
    return {"passed": False, "key": key, "params": {k: _fmt(v) if not isinstance(v, str) else v for k, v in params.items()}}


def check(ns, run_case):
    value, problem = _get(ns, "norm")
    if problem:
        return problem
    if abs(value - np.linalg.norm(V)) > TOL:
        return _fail("norm_wrong", expected=np.linalg.norm(V), actual=value)

    value, problem = _get(ns, "v_hat", (2,))
    if problem:
        return problem
    if not np.allclose(value, V / np.linalg.norm(V), atol=TOL):
        return _fail("v_hat_wrong", expected=V / np.linalg.norm(V), actual=value)

    expected = np.vdot(A, B)
    value, problem = _get(ns, "inner")
    if problem:
        return problem
    if abs(value - expected) > TOL:
        if abs(value - np.conj(expected)) < TOL:
            return _fail("inner_conjugate", actual=value)
        return _fail("inner_wrong", expected=expected, actual=value)

    value, problem = _get(ns, "prob")
    if problem:
        return problem
    if abs(value - abs(expected) ** 2) > TOL:
        return _fail("prob_wrong", expected=abs(expected) ** 2, actual=value)

    value, problem = _get(ns, "minus", (2,))
    if problem:
        return problem
    if abs(np.linalg.norm(value) - 1) > TOL:
        return _fail("minus_not_unit", actual=np.linalg.norm(value))
    overlap = np.vdot(PLUS, value)
    if abs(overlap) > TOL:
        return _fail("minus_not_orthogonal", actual=overlap)
    if not np.allclose(value, MINUS, atol=TOL):
        return _fail("minus_wrong", expected=MINUS, actual=value)

    for name, basis in (("amp_plus", PLUS), ("amp_minus", MINUS)):
        value, problem = _get(ns, name)
        if problem:
            return problem
        expected_amp = np.vdot(basis, PSI)
        if abs(value - expected_amp) > TOL:
            return _fail(name + "_wrong", expected=expected_amp, actual=value)

    value, problem = _get(ns, "inner4")
    if problem:
        return problem
    expected4 = np.vdot(PHI_PLUS, Q)
    if abs(value - expected4) > TOL:
        return _fail("inner4_wrong", expected=expected4, actual=value)

    return {
        "passed": True,
        "key": "ok",
        "params": {"inner": _fmt(expected), "prob": round(float(abs(expected) ** 2), 4),
                   "amp_plus": _fmt(np.vdot(PLUS, PSI)), "amp_minus": _fmt(np.vdot(MINUS, PSI))},
    }
