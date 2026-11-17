"""Challenge for lesson 3.1: the three coefficients of a sinusoidal cost from three evaluations.

`recover(f)` receives a function of one angle and must return (a, b, c, theta_star) for
f(θ) = a cos θ + b sin θ + c, calling f at most three times. The check runs it on three one-qubit
circuits it builds itself (not the visible `mystery`, so a hard-coded answer fails), recomputes
the coefficients from a dense scan and verifies the angle by the value of f there.
"""

import numpy as np
import pennylane as qml

# (angle before, angle after, angle of the final RZ, weight of Z in the observable)
CASES = [(0.9, 0.5, 0.3, 0.5), (-1.3, 2.2, 1.1, -0.8), (0.4, -0.7, 2.5, 1.5)]
TOLERANCE = 1e-6


def _make(case):
    before, after, phase, weight = case
    dev = qml.device("default.qubit", wires=1)

    @qml.qnode(dev)
    def circuit(theta):
        qml.RY(before, wires=0)
        qml.RX(theta, wires=0)
        qml.RY(after, wires=0)
        qml.RZ(phase, wires=0)
        return qml.expval(qml.PauliX(0) + weight * qml.PauliZ(0))

    return lambda theta: float(circuit(theta))


def check(ns, run_case):
    recover = ns.get("recover")
    if not callable(recover):
        return {"passed": False, "key": "ch_no_recover"}
    for case in CASES:
        truth = _make(case)
        calls = []

        def counted(theta, truth=truth, calls=calls):
            calls.append(float(theta))
            return truth(theta)

        try:
            result = recover(counted)
            a, b, c, theta_star = (float(v) for v in result)
        except (TypeError, ValueError):
            return {"passed": False, "key": "ch_bad_return"}
        if len(calls) > 3:
            return {"passed": False, "key": "ch_too_many_calls", "params": {"count": len(calls)}}
        # Exact coefficients from three other points: the cost is a sinusoid, so this is exact.
        c_true = (truth(np.pi / 2) + truth(-np.pi / 2)) / 2
        b_true = (truth(np.pi / 2) - truth(-np.pi / 2)) / 2
        a_true = truth(0.0) - c_true
        if max(abs(a - a_true), abs(b - b_true), abs(c - c_true)) > TOLERANCE:
            return {
                "passed": False,
                "key": "ch_wrong_coefficients",
                "params": {"a": a, "b": b, "c": c, "a_true": a_true, "b_true": b_true, "c_true": c_true},
            }
        minimum = c_true - float(np.hypot(a_true, b_true))
        if abs(truth(theta_star) - minimum) > TOLERANCE:
            return {
                "passed": False,
                "key": "ch_wrong_minimum",
                "params": {"value": truth(theta_star), "minimum": minimum},
            }
    return {"passed": True, "key": "ok", "params": {"minimum": minimum}}
