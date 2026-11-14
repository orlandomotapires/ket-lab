"""Validação da lição 5.4: mitigação de leitura (inversão da matriz de atribuição) e
extrapolação para ruído zero, comparadas com os valores exatos."""

import numpy as np

IDEAL_READOUT = 0.6
IDEAL_CIRCUIT = float(np.cos(0.9))
SCALES = [1, 3, 5]
ZNE_TOLERANCE = 0.006  # o valor bruto erra por 0.023


def number(ns, name):
    try:
        return float(np.real(ns[name]))
    except (KeyError, TypeError, ValueError):
        return None


def check(ns, run_case):
    z_readout = number(ns, "z_readout")
    if z_readout is None:
        return {"passed": False, "key": "missing", "params": {"name": "z_readout"}}
    if abs(z_readout - IDEAL_READOUT) > 1e-6:
        raw = float(ns["p_meas"][0] - ns["p_meas"][1])
        key = "readout_raw" if abs(z_readout - raw) < 1e-9 else "readout_wrong"
        return {"passed": False, "key": key, "params": {"actual": z_readout, "raw": raw}}
    values = ns.get("values")
    expected = [ns["noisy_expectation"](s) for s in SCALES]
    try:
        same = len(values) == 3 and np.allclose([float(v) for v in values], expected, atol=1e-9)
    except (TypeError, ValueError):
        same = False
    if not same:
        return {"passed": False, "key": "wrong_values", "params": {"scales": "1, 3, 5"}}
    zne = number(ns, "zne")
    if zne is None:
        return {"passed": False, "key": "missing", "params": {"name": "zne"}}
    error = abs(zne - IDEAL_CIRCUIT)
    raw_error = abs(expected[0] - IDEAL_CIRCUIT)
    if error > ZNE_TOLERANCE:
        key = "zne_raw" if abs(zne - expected[0]) < 1e-9 else "zne_far"
        return {"passed": False, "key": key, "params": {"actual": zne, "raw": expected[0], "ideal": IDEAL_CIRCUIT}}
    return {"passed": True, "key": "ok", "params": {"error": error, "raw_error": raw_error}}
