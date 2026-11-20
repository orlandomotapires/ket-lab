"""Chart for lesson 3.7: gradient variance against the number of qubits, from `qubits` and `variances`.

When the challenge lists `n_values`, `local_vars` and `global_vars` exist, the two costs at two
layers are drawn on the same axes.
"""


def _numbers(value):
    try:
        values = [float(v) for v in value]
    except (TypeError, ValueError):
        return None
    return values if values and all(v == v and abs(v) != float("inf") for v in values) else None


def analyze(ns):
    series = []
    qubits = _numbers(ns.get("qubits"))
    variances = _numbers(ns.get("variances"))
    # Only the learner's own estimates: the exact decay rate of this ansatz is not part of the lesson.
    if qubits is not None and variances is not None and len(qubits) == len(variances):
        series.append({"label": "Estimated variance", "x": qubits, "y": variances})
    widths = _numbers(ns.get("n_values"))
    for name, label in (("global_vars", "Global cost, 2 layers"), ("local_vars", "Local cost, 2 layers")):
        values = _numbers(ns.get(name))
        if widths is not None and values is not None and len(widths) == len(values):
            series.append({"label": label, "x": widths, "y": values, "dashed": name == "global_vars"})
    if not series:
        return {}
    return {
        "curve": {
            "title": "Variance of the first gradient component",
            "x_label": "qubits",
            "y_label": "variance",
            "log_y": True,
            "series": series,
        }
    }
