"""Validation for lesson 3.7: gradient variance in random circuits.

Does not trust the learner's values: simulates the same ansatz with NumPy, with many
samples, and requires each learner variance to be close to the reference and the
decay with the number of qubits to be the expected one.
"""

import numpy as np

QUBITS = [2, 3, 4, 5, 6]
REFERENCE_SAMPLES = 600
FACTOR = 2.5  # multiplicative tolerance: the learner's 100 samples give about 15% noise


def _reference_variance(n, layers, samples, rng):
    z = np.array([(-1) ** bin(i).count("1") for i in range(2**n)], dtype=float)
    cz = np.empty(2**n)
    for i in range(2**n):
        bits = [(i >> (n - 1 - k)) & 1 for k in range(n)]
        cz[i] = (-1) ** sum(bits[k] & bits[k + 1] for k in range(n - 1))

    def cost(theta):
        psi = np.zeros([2] * n)
        psi[(0,) * n] = 1.0
        for layer in range(layers):
            for q in range(n):
                c, s = np.cos(theta[layer, q] / 2), np.sin(theta[layer, q] / 2)
                psi = np.moveaxis(np.tensordot(np.array([[c, -s], [s, c]]), psi, axes=([1], [q])), 0, q)
            psi = (psi.reshape(-1) * cz).reshape([2] * n)
        flat = psi.reshape(-1)
        return float(flat @ (z * flat))

    grads = []
    for _ in range(samples):
        theta = rng.uniform(0, 2 * np.pi, (layers, n))
        up, down = theta.copy(), theta.copy()
        up[0, 0] += np.pi / 2
        down[0, 0] -= np.pi / 2
        grads.append((cost(up) - cost(down)) / 2)
    return float(np.var(grads))


def check(ns, run_case):
    values = ns.get("variances")
    try:
        values = [float(v) for v in values]
    except (TypeError, ValueError):
        return {"passed": False, "key": "no_variances"}
    if len(values) != len(QUBITS) or not all(np.isfinite(values)) or any(v <= 0 for v in values):
        return {"passed": False, "key": "no_variances", "params": {"count": len(QUBITS)}}
    rng = np.random.default_rng(12345)
    reference = [_reference_variance(n, n, REFERENCE_SAMPLES, rng) for n in QUBITS]
    for n, got, ref in zip(QUBITS, values, reference):
        if not (ref / FACTOR <= got <= ref * FACTOR):
            return {"passed": False, "key": "wrong_value", "params": {"qubits": n, "got": got, "expected": ref}}
    ratio = values[-1] / values[0]
    if ratio > 0.3:
        return {"passed": False, "key": "no_decay", "params": {"ratio": ratio}}
    return {"passed": True, "key": "ok", "params": {"ratio": ratio, "first": values[0], "last": values[-1]}}
