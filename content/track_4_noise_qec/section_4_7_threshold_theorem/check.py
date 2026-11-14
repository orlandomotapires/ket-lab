"""Validação da lição 4.7: concatenação do código de 3 qubits (p ↦ 3p² − 2p³),
modelo genérico (c·p)^(2^k)/c, limiar e número de níveis para um erro alvo.

Os valores esperados vêm da fórmula fechada e de uma iteração própria.
"""

import math


def ref_f(p):
    return 3 * p * p * (1 - p) + p**3  # falha com 2 ou 3 inversões


def ref_concatenated(p, k):
    for _ in range(k):
        p = ref_f(p)
    return p


def ref_levels(p, target):
    if p >= 0.5:
        return None
    k = 0
    while ref_concatenated(p, k) > target:
        k += 1
    return k


def close(a, b, rel=1e-7):
    try:
        return math.isclose(float(a), b, rel_tol=rel, abs_tol=1e-300)
    except (TypeError, ValueError):
        return False


def fail(key, **params):
    return {"passed": False, "key": key, "params": params}


def check(ns, run_case):
    for name in ("f", "concatenated", "generic_rate", "levels_needed"):
        if not callable(ns.get(name)):
            return fail("missing_function", name=name)

    for p in (0.0, 0.01, 0.1, 0.3, 0.5, 0.7, 1.0):
        if not close(ns["f"](p), ref_f(p)) and abs(float(ns["f"](p)) - ref_f(p)) > 1e-12:
            return fail("f_wrong", p=p, want=ref_f(p), got=ns["f"](p))

    for p, k in ((0.01, 0), (0.01, 1), (0.01, 3), (0.1, 2), (0.3, 4), (0.45, 3), (0.6, 3)):
        want = ref_concatenated(p, k)
        if not close(ns["concatenated"](p, k), want):
            return fail("concatenated_wrong", p=p, k=k, want=want, got=ns["concatenated"](p, k))

    for p, c, k in ((0.01, 3, 1), (0.01, 3, 2), (0.05, 10, 3), (0.002, 100, 2)):
        want = (c * p) ** (2**k) / c
        if not close(ns["generic_rate"](p, c, k), want):
            return fail("generic_wrong", p=p, c=c, k=k, want=want, got=ns["generic_rate"](p, c, k))

    for p, target in ((0.01, 1e-15), (0.1, 1e-6), (0.3, 1e-9), (0.01, 0.5), (0.5, 1e-3), (0.6, 1e-3)):
        want = ref_levels(p, target)
        got = ns["levels_needed"](p, target)
        if got != want:
            return fail("levels_wrong", p=p, target=target, want=want, got=got)

    for name in ("p_th", "k_needed", "qubits"):
        if name not in ns:
            return fail("missing", name=name)
    if not close(ns["p_th"], 0.5):
        return fail("threshold_wrong", got=ns["p_th"])
    want_k = ref_levels(0.01, 1e-15)
    if ns["k_needed"] != want_k:
        return fail("k_wrong", got=ns["k_needed"], want=want_k)
    if ns["qubits"] != 3**want_k:
        return fail("qubits_wrong", got=ns["qubits"], k=want_k, want=3**want_k)
    rate = ref_concatenated(0.01, want_k)
    return {"passed": True, "key": "ok", "params": {"k": want_k, "rate": rate, "qubits": 3**want_k, "p_th": 0.5}}
