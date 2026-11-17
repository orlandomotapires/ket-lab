"""Challenge for lesson 5.4: line or parabola for the extrapolation? The check recomputes both
extrapolations from `measured`, their shot noise from `sigma` (the weights of the fit), their bias
from the exact curve `deep_expectation` against `ideal`, and the total expected error
sqrt(bias² + sigma²). For these numbers the line has the smaller total error."""

import numpy as np

SCALES = [1, 3, 5]
NAMES = ("zne_lin", "zne_quad", "sigma_lin", "sigma_quad", "total_lin", "total_quad")


def fit_at_zero(degree, y):
    """Value at scale 0 of the least-squares polynomial, and the weights it puts on the points."""
    weights = np.linalg.pinv(np.vander(SCALES, degree + 1))[-1]
    return float(weights @ np.asarray(y, dtype=float)), weights


def check(ns, run_case):
    got = {}
    for name in NAMES:
        try:
            got[name] = float(np.real(ns[name]))
        except (KeyError, TypeError, ValueError):
            return {"passed": False, "key": "ch_missing", "params": {"name": name}}
    best = ns.get("best")
    if not isinstance(best, str):
        return {"passed": False, "key": "ch_missing", "params": {"name": "best"}}

    measured, sigma, ideal = ns["measured"], float(ns["sigma"]), float(ns["ideal"])
    exact = [ns["deep_expectation"](s) for s in SCALES]
    want = {}
    for tag, degree in (("lin", 1), ("quad", 2)):
        value, weights = fit_at_zero(degree, measured)
        noise = sigma * float(np.sqrt(np.sum(weights**2)))
        bias = fit_at_zero(degree, exact)[0] - ideal
        want["zne_" + tag], want["sigma_" + tag] = value, noise
        want["total_" + tag] = float(np.hypot(bias, noise))
        want["bias_" + tag] = bias

    for tag in ("lin", "quad"):
        if abs(got["zne_" + tag] - want["zne_" + tag]) > 1e-6:
            return {"passed": False, "key": "ch_wrong_zne", "params": {"name": "zne_" + tag, "actual": got["zne_" + tag]}}
    for tag in ("lin", "quad"):
        if abs(got["sigma_" + tag] - want["sigma_" + tag]) > 0.01 * want["sigma_" + tag]:
            key = "ch_sigma_unamplified" if abs(got["sigma_" + tag] - sigma) < 0.01 * sigma else "ch_wrong_sigma"
            return {"passed": False, "key": key, "params": {"name": "sigma_" + tag, "actual": got["sigma_" + tag]}}
    for tag in ("lin", "quad"):
        if abs(got["total_" + tag] - want["total_" + tag]) > 0.01 * want["total_" + tag]:
            key = "ch_no_bias" if abs(got["total_" + tag] - want["sigma_" + tag]) < 0.01 * want["sigma_" + tag] else "ch_wrong_total"
            return {"passed": False, "key": key, "params": {"name": "total_" + tag, "actual": got["total_" + tag]}}
    winner = "linear" if want["total_lin"] < want["total_quad"] else "quadratic"
    if not best.strip().lower().startswith(winner[:4]):
        return {"passed": False, "key": "ch_wrong_best", "params": {"total_lin": got["total_lin"], "total_quad": got["total_quad"]}}
    return {"passed": True, "key": "ch_ok", "params": {"best": winner, "total_lin": want["total_lin"], "total_quad": want["total_quad"]}}
