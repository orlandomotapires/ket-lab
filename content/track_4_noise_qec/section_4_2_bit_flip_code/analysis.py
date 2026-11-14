"""Dados da lição 3.6: a curva de limiar do código de repetição."""

import numpy as np


def analyze(ns):
    p = np.linspace(0, 0.6, 31)
    return {
        "threshold": {
            "x": p,
            "exact": 1 - 3 * p**2 + 2 * p**3,
            "hartree_fock": 1 - p,
            "point": [0.1, 1 - 3 * 0.01 + 2 * 0.001],
            "x_label": "p",
            "y_label": "F",
            "legend": ["viz.withCode", "viz.withoutCode"],
            "note": "viz.thresholdNote",
            "point_label": "viz.pointAtP01",
        }
    }
