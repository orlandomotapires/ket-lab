"""Charts for lesson 6.2: the gap against s, and the success probability against the total time T."""


def _numbers(value):
    try:
        values = [float(v) for v in value]
    except (TypeError, ValueError):
        return None
    return values if values and all(v == v and abs(v) != float("inf") for v in values) else None


def analyze(ns):
    charts = []
    s_grid = _numbers(ns.get("s_grid"))
    gaps = _numbers(ns.get("gaps"))
    if s_grid is not None and gaps is not None and len(s_grid) == len(gaps):
        i_min = min(range(len(gaps)), key=lambda i: gaps[i])
        charts.append(
            {
                "title": "Energy gap along the sweep",
                "x_label": "s",
                "y_label": "gap",
                "series": [{"label": "Gap between the two lowest levels", "x": s_grid, "y": gaps}],
                "markers": [
                    {"x": s_grid[i_min], "y": gaps[i_min], "label": f"smallest gap, {gaps[i_min]:.3f}"}
                ],
            }
        )
    times = _numbers(ns.get("T_values"))
    success = _numbers(ns.get("success"))
    if times is not None and success is not None and len(times) == len(success) and all(t > 0 for t in times):
        charts.append(
            {
                "title": "Success probability against total time",
                "x_label": "total time T",
                "y_label": "probability of |110⟩",
                "log_x": True,
                "series": [{"label": "Success probability", "x": times, "y": success, "points": True}],
            }
        )
    return {"curve": charts} if charts else {}
