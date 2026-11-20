"""Challenge for lesson 3.7: a local cost keeps its gradient at a fixed shallow depth.

The learner writes `local_variance(n, layers, samples)`, the variance of ∂C/∂θ (first angle) for
the cost Z on qubit 0, and stores in `local_vars` and `global_vars` the variances of the local and
the global cost for n_values = [2, 4, 6, 8, 10] with 2 layers and 100 samples. The check
simulates both costs itself (NumPy, seeded, 600 samples), calls the learner's function on an input
it chooses (one layer, where the exact variance of the local cost is 1/2), and requires each stored
value to be near the reference and the local variance to stay near its value at 2 qubits while the
global one falls by a large factor.
"""

import numpy as np

N_VALUES = [2, 4, 6, 8, 10]
LAYERS = 2
REFERENCE_SAMPLES = 600
FACTOR = {"local": 1.8, "global": 4.0}  # 100 samples: the local variance is good to about 20%, the global one has heavy tails

LOCAL_KEEPS = 0.4  # local variance at 10 qubits over that at 2 qubits (reference: about 1)
GLOBAL_FALLS = 0.05  # global variance at 10 qubits over that at 2 qubits (reference: about 0.006)
HIDDEN_CALL = (5, 1, 400)  # n, layers, samples; one layer gives exactly 1/2 for Z on qubit 0
HIDDEN_FACTOR = 1.4


def _reference(n, layers, samples, rng, local):
    size = 2**n
    z = np.array([(-1) ** bin(i).count("1") for i in range(size)], dtype=float)
    z0 = np.array([1 - 2 * ((i >> (n - 1)) & 1) for i in range(size)], dtype=float)  # axis 0 is qubit 0
    cz = np.empty(size)
    for i in range(size):
        bits = [(i >> (n - 1 - k)) & 1 for k in range(n)]
        cz[i] = (-1) ** sum(bits[k] & bits[k + 1] for k in range(n - 1))
    observable = z0 if local else z

    def cost(theta):
        psi = np.zeros([2] * n)
        psi[(0,) * n] = 1.0
        for layer in range(layers):
            for q in range(n):
                c, s = np.cos(theta[layer, q] / 2), np.sin(theta[layer, q] / 2)
                psi = np.moveaxis(np.tensordot(np.array([[c, -s], [s, c]]), psi, axes=([1], [q])), 0, q)
            psi = (psi.reshape(-1) * cz).reshape([2] * n)
        flat = psi.reshape(-1)
        return float(flat @ (observable * flat))

    grads = []
    for _ in range(samples):
        theta = rng.uniform(0, 2 * np.pi, (layers, n))
        up, down = theta.copy(), theta.copy()
        up[0, 0] += np.pi / 2
        down[0, 0] -= np.pi / 2
        grads.append((cost(up) - cost(down)) / 2)
    return float(np.var(grads))


def _numbers(value):
    try:
        values = [float(v) for v in value]
    except (TypeError, ValueError):
        return None
    if len(values) != len(N_VALUES) or not all(np.isfinite(values)) or any(v <= 0 for v in values):
        return None
    return values


def check(ns, run_case):
    function = ns.get("local_variance")
    if not callable(function):
        return {"passed": False, "key": "ch_no_function"}
    local, glob = _numbers(ns.get("local_vars")), _numbers(ns.get("global_vars"))
    try:
        widths = [int(v) for v in ns.get("n_values")]
    except (TypeError, ValueError):
        widths = None
    if local is None or glob is None or widths != N_VALUES:
        return {"passed": False, "key": "ch_no_lists", "params": {"count": len(N_VALUES)}}

    n, layers, samples = HIDDEN_CALL
    try:
        got = float(function(n, layers, samples))
    except Exception:
        return {"passed": False, "key": "ch_function_fails"}
    if not np.isfinite(got) or got <= 0 or not (0.5 / HIDDEN_FACTOR <= got <= 0.5 * HIDDEN_FACTOR):
        return {"passed": False, "key": "ch_wrong_cost", "params": {"got": got if np.isfinite(got) else 0.0}}

    rng = np.random.default_rng(12345)
    ref_local = [_reference(n, LAYERS, REFERENCE_SAMPLES, rng, True) for n in N_VALUES]
    ref_global = [_reference(n, LAYERS, REFERENCE_SAMPLES, rng, False) for n in N_VALUES]
    for name, values, ref in (("local", local, ref_local), ("global", glob, ref_global)):
        for n, value, expected in zip(N_VALUES, values, ref):
            if not (expected / FACTOR[name] <= value <= expected * FACTOR[name]):
                return {
                    "passed": False,
                    "key": "ch_wrong_value",
                    "params": {"which": name, "qubits": n, "got": value, "expected": expected},
                }
    local_ratio = local[-1] / local[0]
    global_ratio = glob[-1] / glob[0]
    if local_ratio < LOCAL_KEEPS or global_ratio > GLOBAL_FALLS:
        return {"passed": False, "key": "ch_no_contrast", "params": {"local": local_ratio, "glob": global_ratio}}
    return {"passed": True, "key": "ok", "params": {"local": local_ratio, "glob": global_ratio}}
