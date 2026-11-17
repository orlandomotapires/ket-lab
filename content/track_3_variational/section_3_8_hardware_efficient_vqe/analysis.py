"""Data for the lesson 3.8 visualization: H₂ energy convergence."""

EXACT = -1.1372838351669659
CHEMICAL_ACCURACY = 1.6e-3


def analyze(ns):
    energies = [float(e) for e in (ns.get("energies") or [])]
    return {"convergence": {"values": energies, "target": EXACT, "band": CHEMICAL_ACCURACY, "y_label": "E (Ha)"}}
