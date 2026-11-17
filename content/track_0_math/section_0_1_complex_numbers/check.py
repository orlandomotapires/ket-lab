"""Validation for lesson 0.1: complex arithmetic, polar form and relative phase."""

import cmath

import numpy as np

TOL = 1e-6
Z, W = 3 + 4j, 1 - 2j
THETA = np.pi / 3
A_PHASE, B_PHASE = 0.9, 1.4


def _fmt(value):
    return np.array2string(np.asarray(value), precision=3, suppress_small=True)


def _scalar(ns, name):
    if name not in ns:
        return None, {"passed": False, "key": "missing", "params": {"name": name}}
    try:
        arr = np.asarray(ns[name], dtype=complex)
        if arr.size != 1:
            raise ValueError
    except (TypeError, ValueError):
        return None, {"passed": False, "key": "not_number", "params": {"name": name, "actual": repr(ns[name])[:40]}}
    return complex(arr.reshape(())), None


def _angle_close(x, y):
    return abs(cmath.exp(1j * (x - y)) - 1) < TOL


def check(ns, run_case):
    steps = [
        ("product", Z * W, "product_wrong"),
        ("modulus", 5.0, "modulus_wrong"),
        ("phi", cmath.phase(Z), "phi_wrong"),
        ("z_polar", Z, "z_polar_wrong"),
        ("unit", cmath.exp(1j * THETA), "unit_wrong"),
        ("unit_modulus", 1.0, "unit_modulus_wrong"),
    ]
    for name, expected, key in steps:
        value, problem = _scalar(ns, name)
        if problem:
            return problem
        if abs(value - expected) > TOL:
            return {"passed": False, "key": key, "params": {"expected": _fmt(expected), "actual": _fmt(value)}}
    value, problem = _scalar(ns, "rel_phase")
    if problem:
        return problem
    expected = B_PHASE - A_PHASE
    if abs(value.imag) > TOL or not _angle_close(value.real, expected):
        if abs(value.imag) < TOL and _angle_close(value.real, B_PHASE):
            return {"passed": False, "key": "rel_phase_single", "params": {"actual": _fmt(value.real)}}
        return {"passed": False, "key": "rel_phase_wrong", "params": {"expected": _fmt(expected), "actual": _fmt(value)}}
    return {
        "passed": True,
        "key": "ok",
        "params": {"modulus": 5, "phi": round(cmath.phase(Z), 4), "unit_modulus": 1, "rel_phase": round(expected, 4)},
    }
