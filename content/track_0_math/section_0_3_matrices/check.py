"""Validation for lesson 0.3: unitarity, Pauli, eigenvalues, Hermitian matrices, expectation value."""

import numpy as np

TOL = 1e-6
A = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
B = np.array([[1, 1], [0, 1]])
X = np.array([[0, 1], [1, 0]])
Z = np.array([[1, 0], [0, -1]])
Y = np.array([[0, -1j], [1j, 0]])
PSI = np.array([0.6, 0.8j])


def _fmt(value):
    return np.array2string(np.asarray(value), precision=3, suppress_small=True, separator=", ")


def _fail(key, **params):
    return {"passed": False, "key": key, "params": {k: v if isinstance(v, str) else _fmt(v) for k, v in params.items()}}


def _get(ns, name, shape=()):
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


def _get_bool(ns, name):
    if name not in ns:
        return None, {"passed": False, "key": "missing", "params": {"name": name}}
    if not isinstance(ns[name], (bool, np.bool_)):
        return None, {"passed": False, "key": "not_bool", "params": {"name": name, "actual": repr(ns[name])[:40]}}
    return bool(ns[name]), None


def check(ns, run_case):
    value, problem = _get(ns, "Y", (2, 2))
    if problem:
        return problem
    if not np.allclose(value, Y, atol=TOL):
        return _fail("y_wrong", actual=value)

    flag, problem = _get_bool(ns, "a_unitary")
    if problem:
        return problem
    if flag is not True:
        return _fail("a_unitary_wrong")
    flag, problem = _get_bool(ns, "b_unitary")
    if problem:
        return problem
    if flag is not False:
        return _fail("b_unitary_wrong", product=B.conj().T @ B)

    vals, problem = _get(ns, "eigvals", (2,))
    if problem:
        return problem
    if np.max(np.abs(vals.imag)) > TOL or not np.allclose(np.sort(vals.real), [-1, 1], atol=TOL):
        return _fail("eigvals_wrong", actual=vals)
    vecs, problem = _get(ns, "eigvecs", (2, 2))
    if problem:
        return problem
    for k in range(2):
        v = vecs[:, k]
        if np.linalg.norm(v) < TOL or not np.allclose(X @ v, vals[k] * v, atol=TOL):
            return _fail("eigvecs_wrong", column=str(k))

    flag, problem = _get_bool(ns, "k_hermitian")
    if problem:
        return problem
    if flag is not True:
        return _fail("k_hermitian_wrong")

    value, problem = _get(ns, "expect_z")
    if problem:
        return problem
    expected_z = np.vdot(PSI, Z @ PSI)
    if abs(value - expected_z) > TOL:
        return _fail("expect_z_wrong", expected=expected_z.real, actual=value.real if abs(value.imag) < TOL else value)

    value, problem = _get(ns, "expect_y")
    if problem:
        return problem
    expected_y = np.vdot(PSI, Y @ PSI)
    if abs(value - expected_y) > TOL:
        actual = value.real if abs(value.imag) < TOL else value
        if abs(value - PSI @ (Y @ PSI)) < TOL:
            return _fail("expect_y_no_conjugate", actual=actual)
        return _fail("expect_y_wrong", expected=expected_y.real, actual=actual)

    return {
        "passed": True,
        "key": "ok",
        "params": {"eigvals": "−1 and 1", "expect_z": round(float(expected_z.real), 4), "expect_y": round(float(expected_y.real), 4)},
    }
