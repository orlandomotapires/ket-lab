"""Challenge for lesson 6.2: the Landau–Zener formula against a simulated sweep.

H(t) = (v t / 2) Z + (Δ / 2) X for t from −T to T, ħ = 1, starting in the ground state of H(−T).
The learner writes landau_zener(v, delta) = exp(−π Δ² / (2 v)) and
sweep_probability(v, delta, T, n_steps), the probability of the excited eigenstate of H(T) after
the sweep, and stores rates = [0.5, 1, 2, 4], simulated and predicted for Δ = 1, T = 20, 2000 steps.
The check calls both functions on (v, Δ) pairs of its own and recomputes the stored lists. At
T = 20 the simulated probability agrees with the formula to about 3e-4 (reference), while a
readout in |0⟩ instead of the excited eigenstate is off by up to 0.02, so a tolerance of 2e-3
accepts every correct simulation and rejects that readout.
"""

import numpy as np

X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
RATES = [0.5, 1, 2, 4]
T_SWEEP, STEPS = 20, 2000
HIDDEN_CASES = [(1.5, 0.8), (0.6, 0.5), (3.0, 1.2)]  # (v, Δ)
TOLERANCE = 2e-3


def ref_formula(v, delta):
    return float(np.exp(-np.pi * delta**2 / (2 * v)))


def _ham(t, v, delta):
    return (v * t / 2) * Z + (delta / 2) * X


def ref_sweep(v, delta, T=T_SWEEP, n=STEPS, readout="excited"):
    dt = 2 * T / n
    psi = np.linalg.eigh(_ham(-T, v, delta))[1][:, 0]
    for k in range(n):
        w, u = np.linalg.eigh(_ham(-T + (k + 0.5) * dt, v, delta))
        psi = u @ (np.exp(-1j * w * dt) * (u.conj().T @ psi))
    if readout == "diabatic":
        return float(abs(psi[0]) ** 2)
    return float(abs(np.linalg.eigh(_ham(T, v, delta))[1][:, 1].conj() @ psi) ** 2)


def _number(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None


def _list(value, size):
    try:
        values = [float(v) for v in value]
    except (TypeError, ValueError):
        return None
    return values if len(values) == size and all(np.isfinite(values)) else None


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def check(ns, run_case):
    for name in ("landau_zener", "sweep_probability"):
        if not callable(ns.get(name)):
            return fail("ch_missing_function", name=name)

    for v, delta in HIDDEN_CASES:
        want = ref_formula(v, delta)
        try:
            got = _number(ns["landau_zener"](v, delta))
        except Exception:
            got = None
        if got is None or abs(got - want) > 1e-6:
            return fail("ch_formula_wrong", v=v, delta=delta, want=want, got=got if got is not None else "no number")

    for v, delta in HIDDEN_CASES[:2]:
        try:
            got = _number(ns["sweep_probability"](v, delta, T_SWEEP, STEPS))
        except Exception:
            got = None
        if got is None:
            return fail("ch_sweep_fails", v=v, delta=delta)
        want = ref_sweep(v, delta)
        if abs(got - want) > TOLERANCE:
            if abs(got - ref_sweep(v, delta, readout="diabatic")) <= TOLERANCE:
                return fail("ch_readout", v=v, delta=delta)
            if abs(got - (1 - want)) <= TOLERANCE:
                return fail("ch_complement", v=v, delta=delta)
            return fail("ch_sweep_wrong", v=v, delta=delta, want=want, got=got)

    simulated = _list(ns.get("simulated"), len(RATES))
    predicted = _list(ns.get("predicted"), len(RATES))
    try:
        rates_ok = [float(r) for r in ns.get("rates")] == [float(r) for r in RATES]
    except (TypeError, ValueError):
        rates_ok = False
    if simulated is None or predicted is None or not rates_ok:
        return fail("ch_lists", count=len(RATES))
    for v, got in zip(RATES, predicted):
        if abs(got - ref_formula(v, 1.0)) > 1e-6:
            return fail("ch_predicted_wrong", v=v, want=ref_formula(v, 1.0), got=got)
    for v, got in zip(RATES, simulated):
        want = ref_sweep(v, 1.0)
        if abs(got - want) > TOLERANCE:
            return fail("ch_simulated_wrong", v=v, want=want, got=got)
    return {
        "passed": True,
        "key": "ok",
        "params": {"worst": max(abs(a - b) for a, b in zip(simulated, predicted)), "slow": simulated[0], "fast": simulated[-1]},
    }
