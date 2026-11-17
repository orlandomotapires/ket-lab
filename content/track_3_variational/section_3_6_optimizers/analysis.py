"""Chart for lesson 3.6: the cost after each SPSA step, from the learner's `energies` list."""


def _numbers(value):
    try:
        values = [float(v) for v in value]
    except (TypeError, ValueError):
        return None
    return values if values and all(v == v and abs(v) != float("inf") for v in values) else None


def analyze(ns):
    energies = _numbers(ns.get("energies"))
    if energies is None:
        return {}
    steps = list(range(len(energies)))
    series = [{"label": "Cost after each step", "x": steps, "y": energies}]
    # Reference: the lowest value the cost can take for this circuit.
    series.append({"label": "Minimum, −1", "x": [0, max(steps[-1], 1)], "y": [-1.0, -1.0], "dashed": True})
    return {"curve": {"title": "Cost during SPSA", "x_label": "step", "y_label": "cost", "series": series}}
