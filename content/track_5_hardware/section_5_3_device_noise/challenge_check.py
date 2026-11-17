"""Challenge for lesson 5.3: estimate T1, T2 and the pure dephasing time from noisy decay data.
The hidden setup draws the data from T1 = 120 µs and T2 = 70 µs (so Tφ = 98.8 µs) with noise
of 0.004 on every point. The check does not trust the data in the namespace: it compares the
learner's numbers with the true times, with tolerances that a log-linear fit meets."""

TRUE_T1, TRUE_T2 = 120.0, 70.0
TRUE_TPHI = 1 / (1 / TRUE_T2 - 1 / (2 * TRUE_T1))
TOLERANCE = {"T1_fit": 0.10, "T2_fit": 0.10, "Tphi_fit": 0.20}
TRUE = {"T1_fit": TRUE_T1, "T2_fit": TRUE_T2, "Tphi_fit": TRUE_TPHI}


def check(ns, run_case):
    values = {}
    for name in ("T1_fit", "T2_fit", "Tphi_fit"):
        try:
            values[name] = float(ns[name])
        except (KeyError, TypeError, ValueError):
            return {"passed": False, "key": "ch_missing", "params": {"name": name}}
    t1, t2, tphi = values["T1_fit"], values["T2_fit"], values["Tphi_fit"]
    if not all(v > 0 and v == v for v in (t1, t2, tphi)) or t2 > 2 * t1:
        return {"passed": False, "key": "ch_unphysical", "params": {"T1": t1, "T2": t2}}
    for name in ("T1_fit", "T2_fit"):
        if abs(values[name] - TRUE[name]) > TOLERANCE[name] * TRUE[name]:
            return {"passed": False, "key": "ch_far_" + name[:2].lower(), "params": {"actual": values[name]}}
    implied = 1 / (1 / t2 - 1 / (2 * t1))
    if abs(tphi - implied) > 0.01 * implied:
        return {"passed": False, "key": "ch_inconsistent", "params": {"tphi": tphi, "implied": implied}}
    if abs(tphi - TRUE_TPHI) > TOLERANCE["Tphi_fit"] * TRUE_TPHI:
        return {"passed": False, "key": "ch_far_tphi", "params": {"actual": tphi}}
    return {"passed": True, "key": "ch_ok", "params": {"T1": t1, "T2": t2, "tphi": tphi}}
