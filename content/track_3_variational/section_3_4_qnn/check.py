"""Validation for lesson 3.4: accuracy on a test set the learner never sees,
computed with the learner's circuit and final weights (not with reported values)."""

import numpy as np

from ket_lab_engine import pl

THRESHOLD = 0.92
LAYERS_MIN_UPLOADS = 8  # data re-uploads (RX/RY with x): at least 2 layers on 2 qubits

def make_circles(n, seed):
    """Two concentric circles: radius 1.0 (class +1) and 0.45 (class -1), with radial noise."""
    import numpy as _np

    rng = _np.random.default_rng(seed)
    labels = _np.where(_np.arange(n) % 2 == 0, 1.0, -1.0)
    radius = _np.where(labels > 0, 1.0, 0.45) + rng.normal(0, 0.08, n)
    angle = rng.uniform(0, 2 * _np.pi, n)
    points = _np.stack([radius * _np.cos(angle), radius * _np.sin(angle)], axis=1)
    return points, labels


def accuracy(circuit, weights, points, labels):
    outputs = np.asarray(circuit(weights, points), dtype=float)
    return float(np.mean(np.sign(outputs) == labels))


def data_uploads(circuit, weights, sample):
    ops, _, _ = pl.trace_qnode(circuit, [weights, sample])
    values = [float(v) for v in np.asarray(sample).reshape(-1)]
    return sum(1 for op in ops if op.params and any(abs(op.params[0] - v) < 1e-9 for v in values))


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    if "weights" not in ns:
        return {"passed": False, "key": "no_weights"}
    weights = ns["weights"]
    test_x, test_y = make_circles(200, seed=2024)
    train_x, train_y = make_circles(80, seed=7)
    test_acc = accuracy(circuit, weights, test_x, test_y)
    train_acc = accuracy(circuit, weights, train_x, train_y)
    params = {"test": test_acc * 100, "train": train_acc * 100, "threshold": THRESHOLD * 100}
    if test_acc >= THRESHOLD:
        return {"passed": True, "key": "ok", "params": params}
    if train_acc >= 0.95:
        return {"passed": False, "key": "overfit", "params": params}
    uploads = data_uploads(circuit, weights, test_x[:1])
    if uploads < LAYERS_MIN_UPLOADS:
        return {"passed": False, "key": "no_reupload", "params": {**params, "uploads": uploads}}
    return {"passed": False, "key": "low_accuracy", "params": params}
