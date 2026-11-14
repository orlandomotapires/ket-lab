"""Dados das visualizações da lição 3.2: convergência e curva de dissociação do H₂."""

EXACT = -1.1372838351669659
CHEMICAL_ACCURACY = 1.6e-3
BOND = 0.74

# distância (Å), energia exata (Ha), energia Hartree-Fock (Ha), STO-3G
CURVE = [[0.3, -0.601804, -0.593828], [0.4, -0.91415, -0.904361], [0.5, -1.05516, -1.042996], [0.6, -1.116286, -1.101128], [0.7, -1.136189, -1.117349], [0.8, -1.134148, -1.11085], [0.9, -1.12056, -1.091914], [1.0, -1.10115, -1.066109], [1.1, -1.079193, -1.036539], [1.2, -1.056741, -1.005107], [1.3, -1.035186, -0.973111], [1.4, -1.015468, -0.941481], [1.5, -0.998149, -0.910874], [1.6, -0.983473, -0.881732], [1.7, -0.971427, -0.854338], [1.8, -0.961817, -0.828848], [1.9, -0.954339, -0.805333], [2.0, -0.948641, -0.783793], [2.1, -0.944375, -0.764178], [2.2, -0.941224, -0.746401], [2.3, -0.938922, -0.730353], [2.4, -0.937255, -0.71591], [2.5, -0.936055, -0.702944]]


def analyze(ns):
    energies = [float(e) for e in (ns.get("energies") or [])]
    final = energies[-1] if energies else None
    return {
        "convergence": {
            "values": energies,
            "target": EXACT,
            "band": CHEMICAL_ACCURACY,
            "y_label": "E (Ha)",
        },
        "dissociation": {
            "x": [row[0] for row in CURVE],
            "exact": [row[1] for row in CURVE],
            "hartree_fock": [row[2] for row in CURVE],
            "point": [BOND, final] if final is not None else None,
            "x_label": "d (Å)",
            "y_label": "E (Ha)",
        },
    }
