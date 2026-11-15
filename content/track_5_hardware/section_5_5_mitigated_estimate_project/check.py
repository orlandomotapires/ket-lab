"""Validação do projeto 5.5 (estimativa mitigada num dispositivo ruidoso): rubrica com seis critérios.

1. ghz prepara o estado GHZ só com h, x e cx entre vizinhos;
2. fold dobra o circuito corretamente (escalas 1, 3, 5, 7, em dois circuitos);
3. A concorda com a matriz de atribuição verdadeira;
4. raw concorda com o valor ruidoso exato dentro de cinco larguras de ruído de tiros;
5. o erro do valor mitigado é no máximo 1/5 do erro bruto;
6. sigma concorda com a dispersão de uma execução independente da mesma estimativa
   (leitura mitigada + extrapolação linear, mesmo número de tiros).
"""

import numpy as np

SCALES = [1, 3, 5]
MAX_RAW_RATIO = 5
A_TOLERANCE = 0.02
SIGMA_LOW, SIGMA_HIGH = 0.4, 3.0
SIGN = np.array([(-1) ** (int(format(i, "03b")[0]) + int(format(i, "03b")[2])) for i in range(8)])
OTHER = [("h", 1), ("cx", 1, 2), ("x", 0)]


def number(ns, name):
    try:
        return float(np.real(ns[name]))
    except (KeyError, TypeError, ValueError):
        return None


def fold_reference(gates, scale):
    gates = [tuple(g) for g in gates]
    return gates + (gates[::-1] + gates) * ((scale - 1) // 2)


def reference_sigma(ns, shots, repeats=40):
    """Dispersão da estimativa de referência com a verdade exata de A (sem erro de calibração)."""
    ghz = [tuple(g) for g in ns["ghz"]]
    a_inv = np.linalg.inv(np.kron(np.kron(ns["_READ"], ns["_READ"]), ns["_READ"]))
    probs = [ns["_probabilities"](fold_reference(ghz, s)) for s in SCALES]
    estimates = []
    for seed in range(repeats):
        rng = np.random.default_rng(1000 + seed)
        values = [float(SIGN @ (a_inv @ (rng.multinomial(shots, p) / shots))) for p in probs]
        estimates.append(np.polyval(np.polyfit(SCALES, values, 1), 0))
    return float(np.std(estimates, ddof=1))


def check(ns, run_case):
    for name in ("ghz", "fold", "A", "raw", "mitigated", "sigma"):
        if name not in ns or (name == "fold" and not callable(ns["fold"])):
            return {"passed": False, "key": "missing", "params": {"name": name}}
    ghz = [tuple(g) for g in ns["ghz"]]
    try:
        ideal = ns["_probabilities"](ghz, noisy=False)
    except Exception as exc:  # noqa: BLE001
        return {"passed": False, "key": "circuit", "params": {"detail": str(exc)}}
    if not np.allclose(ideal, [0.5, 0, 0, 0, 0, 0, 0, 0.5], atol=1e-9):
        return {"passed": False, "key": "circuit", "params": {"detail": "the output distribution is not 50% 000 and 50% 111"}}
    for gates in (ghz, OTHER):
        for scale in (1, 3, 5, 7):
            try:
                actual = [tuple(g) for g in ns["fold"](list(gates), scale)]
            except Exception:  # noqa: BLE001
                actual = None
            if actual != fold_reference(gates, scale):
                return {"passed": False, "key": "folding", "params": {"scale": scale, "gates": str(gates), "actual": str(actual)}}
    shots = ns.get("shots")
    if not isinstance(shots, (int, np.integer)) or isinstance(shots, bool) or not 5000 <= shots <= 200000:
        return {"passed": False, "key": "shots", "params": {"actual": shots}}
    try:
        matrix = np.asarray(ns["A"], dtype=float)
        exact = np.kron(np.kron(ns["_READ"], ns["_READ"]), ns["_READ"])
        error = float(np.max(np.abs(matrix - exact))) if matrix.shape == (8, 8) else float("inf")
    except (TypeError, ValueError):
        error = float("inf")
    if error > A_TOLERANCE:
        return {"passed": False, "key": "readout", "params": {"error": error}}
    raw = number(ns, "raw")
    expected = float(SIGN @ ns["_probabilities"](ghz))
    tolerance = 5 / np.sqrt(shots)
    if raw is None or abs(raw - expected) > tolerance:
        return {"passed": False, "key": "raw", "params": {"actual": raw, "expected": expected, "tolerance": tolerance}}
    mitigated = number(ns, "mitigated")
    raw_error, mitigated_error = abs(raw - 1.0), abs((mitigated if mitigated is not None else raw) - 1.0)
    if mitigated is None or mitigated_error > raw_error / MAX_RAW_RATIO:
        return {"passed": False, "key": "mitigated", "params": {"mitigated_error": mitigated_error, "raw_error": raw_error}}
    sigma = number(ns, "sigma")
    reference = reference_sigma(ns, int(shots))
    low, high = SIGMA_LOW * reference, SIGMA_HIGH * reference
    if sigma is None or not low <= sigma <= high:
        return {"passed": False, "key": "sigma", "params": {"actual": sigma, "expected": reference, "low": low, "high": high}}
    return {"passed": True, "key": "ok", "params": {"raw": raw, "raw_error": raw_error, "mitigated": mitigated, "mitigated_error": mitigated_error, "sigma": sigma, "reference_sigma": reference}}
