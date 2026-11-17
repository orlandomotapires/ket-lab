"""Validation for project 3.9 (variational dissociation curve of H₂).

Rubric: (1) complete data, ≥ 5 distances between 0.5 and 2.0 Å, ≥ 3 of them between 0.5 and
1.0; (2) at most 40 steps per distance; (3) the ansatz is the chemistry one and the reported
energies match the ones recomputed here from the angles, without falling below the exact
energy; (4) each recomputed energy is within 1.6 mHa of the exact one (Hamiltonian
diagonalization); (5) r_eq is within 0.05 Å of the exact minimum.
"""

import numpy as np
import pennylane as qml

from qlp_engine import pl

CHEMICAL_ACCURACY = 1.6e-3
MAX_STEPS = 40
BOHR_PER_ANGSTROM = 1.0 / 0.529177210903
EQUILIBRIUM = 0.734  # exact minimum of the STO-3G curve (scan with a 0.002 Å step)
EQUILIBRIUM_TOLERANCE = 0.05
CONSISTENCY = 1e-6


def exact_hamiltonian(distance):
    coordinates = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, float(distance) * BOHR_PER_ANGSTROM]])
    molecule = qml.qchem.Molecule(["H", "H"], coordinates, basis_name="sto-3g")
    hamiltonian = qml.qchem.molecular_hamiltonian(molecule, method="dhf")[0]
    return qml.matrix(hamiltonian, wire_order=range(4))


def ansatz_energy(matrix, theta):
    """⟨ψ|H|ψ⟩ for cos(θ/2)|1100⟩ − sin(θ/2)|0011⟩ (wire 0 is the most significant bit)."""
    state = np.zeros(16, dtype=complex)
    state[0b1100] = np.cos(theta / 2)
    state[0b0011] = -np.sin(theta / 2)
    return float(np.real(np.vdot(state, matrix @ state)))


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    names = ("distances", "thetas", "histories", "energies")
    if any(not isinstance(ns.get(name), (list, tuple)) for name in names):
        return {"passed": False, "key": "no_data"}
    distances = [float(d) for d in ns["distances"]]
    thetas = [float(x) for x in ns["thetas"]]
    histories = [[float(e) for e in h] for h in ns["histories"]]
    energies = [float(e) for e in ns["energies"]]
    count = len(distances)
    if not (len(thetas) == len(histories) == len(energies) == count) or any(not h for h in histories):
        return {"passed": False, "key": "lengths", "params": {"count": count}}

    near = [d for d in distances if 0.5 <= d <= 1.0]
    if (
        count < 5
        or len(set(distances)) < count
        or min(distances) < 0.5
        or max(distances) > 2.0
        or len(near) < 3
    ):
        return {"passed": False, "key": "distances", "params": {"count": count}}

    for d, history in zip(distances, histories):
        if len(history) - 1 > MAX_STEPS:
            return {"passed": False, "key": "budget", "params": {"distance": d, "steps": len(history) - 1}}

    if "theta" not in ns:
        return {"passed": False, "key": "no_theta"}
    ops, _, n = pl.trace_qnode(circuit, [ns["theta"]])
    extra = sorted({op.name for op in ops} - {"x", "id", "singleexcitation", "doubleexcitation"})
    if n != 4 or extra:
        return {"passed": False, "key": "forbidden_op", "params": {"names": ", ".join(extra) or f"{n} qubits"}}

    errors = []
    for d, theta, history, energy in zip(distances, thetas, histories, energies):
        matrix = exact_hamiltonian(d)
        exact = float(np.linalg.eigvalsh(matrix)[0])
        recomputed = ansatz_energy(matrix, theta)
        if min(energy, history[-1]) < exact - CONSISTENCY:
            return {
                "passed": False, "key": "below_exact",
                "params": {"distance": d, "energy": min(energy, history[-1]), "exact": exact},
            }
        if abs(energy - recomputed) > CONSISTENCY or abs(history[-1] - recomputed) > CONSISTENCY:
            return {
                "passed": False, "key": "inconsistent",
                "params": {"distance": d, "energy": energy, "recomputed": recomputed},
            }
        errors.append((d, recomputed - exact))

    bad = [(d, e) for d, e in errors if e > CHEMICAL_ACCURACY]
    if bad:
        worst_d, worst_e = max(bad, key=lambda item: item[1])
        return {
            "passed": False, "key": "accuracy",
            "params": {"bad": len(bad), "count": count, "distance": worst_d, "error": worst_e},
        }

    r_eq = ns.get("r_eq")
    if not isinstance(r_eq, (int, float)) or isinstance(r_eq, bool) or not np.isfinite(r_eq):
        return {"passed": False, "key": "no_r_eq"}
    if abs(float(r_eq) - EQUILIBRIUM) > EQUILIBRIUM_TOLERANCE:
        return {"passed": False, "key": "r_eq_wrong", "params": {"value": float(r_eq), "exact": EQUILIBRIUM}}
    return {
        "passed": True, "key": "ok",
        "params": {"count": count, "worst": max(e for _, e in errors), "r_eq": float(r_eq), "exact": EQUILIBRIUM},
    }
