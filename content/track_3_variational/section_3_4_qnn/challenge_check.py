"""Challenge for lesson 3.4: the same circles with a single qubit.

The check traces the learner's circuit and requires every gate to act on one and the same qubit (a
one-wire device that is used, or a larger device of which only one wire is touched). It then measures the
accuracy of sign(<Z>) with the learner's final weights on 300 points of the same two circles drawn with a
seed that neither the mission nor the training set uses, so the weights cannot have seen them. A circuit
that fails to run or returns the wrong shape maps to a message key, never to an error.
"""

import numpy as np

from ket_lab_engine import pl

THRESHOLD = 0.90
TEST_SEED = 4711
TRAIN_SEED = 7  # the training set of the lesson, to tell memorizing from not learning


def make_circles(n, seed):
    """Two concentric circles: radius 1.0 (class +1) and 0.45 (class -1), with radial noise."""
    rng = np.random.default_rng(seed)
    labels = np.where(np.arange(n) % 2 == 0, 1.0, -1.0)
    radius = np.where(labels > 0, 1.0, 0.45) + rng.normal(0, 0.08, n)
    angle = rng.uniform(0, 2 * np.pi, n)
    points = np.stack([radius * np.cos(angle), radius * np.sin(angle)], axis=1)
    return points, labels


def _accuracy(circuit, weights, points, labels):
    outputs = np.asarray(circuit(weights, points), dtype=float).reshape(-1)
    if outputs.shape != labels.shape or not np.all(np.isfinite(outputs)):
        raise ValueError("wrong output shape")
    return float(np.mean(np.sign(outputs) == labels))


def _uploads(ops, sample):
    values = [float(v) for v in np.asarray(sample).reshape(-1)]
    count = 0
    for op in ops:
        if op.params and np.size(op.params[0]) == 1 and any(abs(float(np.ravel(op.params[0])[0]) - v) < 1e-9 for v in values):
            count += 1
    return count


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "ch_no_circuit"}
    if "weights" not in ns:
        return {"passed": False, "key": "ch_no_weights"}
    weights = ns["weights"]
    test_x, test_y = make_circles(300, TEST_SEED)
    train_x, train_y = make_circles(80, TRAIN_SEED)
    try:
        ops, _, _ = pl.trace_qnode(circuit, [weights, test_x[:1]])
    except Exception:  # noqa: BLE001 - unfinished learner code
        return {"passed": False, "key": "ch_error"}
    used = sorted({q for op in ops for q in op.qubits})
    if len(used) > 1:
        return {"passed": False, "key": "ch_more_qubits", "params": {"count": len(used)}}
    try:
        test_acc = _accuracy(circuit, weights, test_x, test_y)
        train_acc = _accuracy(circuit, weights, train_x, train_y)
    except Exception:  # noqa: BLE001 - unfinished learner code
        return {"passed": False, "key": "ch_error"}
    params = {"test": test_acc * 100, "train": train_acc * 100, "threshold": THRESHOLD * 100}
    if test_acc >= THRESHOLD:
        return {"passed": True, "key": "ok", "params": params}
    if train_acc >= 0.95:
        return {"passed": False, "key": "ch_overfit", "params": params}
    uploads = _uploads(ops, test_x[:1])
    if uploads < 4:
        return {"passed": False, "key": "ch_no_reupload", "params": {**params, "uploads": uploads}}
    return {"passed": False, "key": "ch_low_accuracy", "params": params}
