"""Chart for lesson 3.7: gradient variance against the number of qubits, from `qubits` and `variances`."""


def _numbers(value):
    try:
        values = [float(v) for v in value]
    except (TypeError, ValueError):
        return None
    return values if values and all(v == v and abs(v) != float("inf") for v in values) else None


def analyze(ns):
    qubits = _numbers(ns.get("qubits"))
    variances = _numbers(ns.get("variances"))
    if qubits is None or variances is None or len(qubits) != len(variances):
        return {}
    # Only the learner's own estimates: the exact decay rate of this ansatz is not part of the lesson.
    return {
        "curve": {
            "title": "Variance of the first gradient component",
            "x_label": "qubits",
            "y_label": "variance",
            "log_y": True,
            "series": [{"label": "Estimated variance", "x": qubits, "y": variances}],
        }
    }
