"""Challenge for lesson 3.8: the all-zero start of the hardware-efficient ansatz.

The learner reports the energy, the gradient norm and an optimizer run from theta = 0, and then trains
from a better start. The check does not trust the reported numbers: it traces the learner's circuit at
zero angles, computes the energy with its own Hamiltonian and the gradient by central differences, and
requires the final energy to be within chemical accuracy as in the mission.
"""

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

from qlp_engine import pl, simulator

EXACT = -1.1372838351669659
CHEMICAL_ACCURACY = 1.6e-3
ROTATIONS = {"rx", "ry", "rz"}
ALLOWED = ROTATIONS | {"x", "id", "cx", "cz", "cy", "crx", "cry", "crz", "rzz", "h"}
MAX_ANGLES = 16
ANGLES = 16
STEP = 1e-4
FLAT = 1e-6

TERMS = [
    (-0.0970662078, 'IIII'), (0.171412835, 'ZIII'), (0.171412835, 'IZII'), (0.1686889846, 'ZZII'),
    (-0.2234315573, 'IIZI'), (0.1206252378, 'ZIZI'), (0.1659278524, 'IZZI'), (0.0453026146, 'YXXY'),
    (-0.0453026146, 'YYXX'), (-0.0453026146, 'XXYY'), (0.0453026146, 'XYYX'), (-0.2234315573, 'IIIZ'),
    (0.1659278524, 'ZIIZ'), (0.1206252378, 'IZIZ'), (0.1744128778, 'IIZZ'),
]


def _hamiltonian_matrix():
    ops = [qml.pauli.string_to_pauli_word(word) for _, word in TERMS]
    return qml.matrix(qml.Hamiltonian([c for c, _ in TERMS], ops), wire_order=range(4))


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "ch_no_circuit"}
    if "theta" not in ns:
        return {"passed": False, "key": "ch_no_theta"}
    for name in ("energy_zero", "grad_norm_zero", "energies_zero"):
        if name not in ns:
            return {"passed": False, "key": "ch_missing_report", "params": {"name": name}}
    matrix = _hamiltonian_matrix()

    def energy_of(theta):
        ops, lines, n = pl.trace_qnode(circuit, [pnp.array(theta, requires_grad=False)])
        state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
        state = state.reshape((2,) * n).transpose(range(n)[::-1]).reshape(-1)
        return float(np.real(np.vdot(state, matrix @ state)))

    # The starting point of the experiment: all sixteen angles at zero.
    zero = np.zeros(ANGLES)
    energy0 = energy_of(zero)
    gradient = np.array([
        (energy_of(zero + STEP * e) - energy_of(zero - STEP * e)) / (2 * STEP) for e in np.eye(ANGLES)
    ])
    grad_norm = float(np.linalg.norm(gradient))
    if grad_norm > FLAT:
        return {"passed": False, "key": "ch_zero_not_flat", "params": {"norm": grad_norm}}
    if abs(float(ns["energy_zero"]) - energy0) > 1e-5:
        return {"passed": False, "key": "ch_energy_zero_wrong", "params": {"reported": float(ns["energy_zero"]), "energy": energy0}}
    if abs(float(ns["grad_norm_zero"])) > FLAT:
        return {"passed": False, "key": "ch_grad_wrong", "params": {"reported": float(ns["grad_norm_zero"])}}
    history = [float(e) for e in ns["energies_zero"]]
    if len(history) < 10:
        return {"passed": False, "key": "ch_zero_run_short", "params": {"count": len(history)}}
    if max(abs(e - energy0) for e in history) > 1e-6:
        return {"passed": False, "key": "ch_zero_run_moved", "params": {"energy": energy0}}
    # The second half: the same checks as the mission on the final angles.
    ops, lines, n = pl.trace_qnode(circuit, [ns["theta"]])
    if n != 4:
        return {"passed": False, "key": "ch_wrong_qubits", "params": {"count": n}}
    extra = sorted({op.name for op in ops} - ALLOWED)
    if extra:
        return {"passed": False, "key": "ch_forbidden_op", "params": {"names": ", ".join(extra)}}
    angles = sum(1 for op in ops if op.name in ROTATIONS)
    if angles > MAX_ANGLES:
        return {"passed": False, "key": "ch_too_many_angles", "params": {"count": angles, "limit": MAX_ANGLES}}
    energy = energy_of(np.array(ns["theta"], dtype=float))
    error = energy - EXACT
    params = {"energy": energy, "error": abs(error), "stuck": energy0}
    if error > CHEMICAL_ACCURACY:
        return {"passed": False, "key": "ch_not_converged", "params": params}
    energies = ns.get("energies") or []
    if not energies or abs(float(energies[-1]) - energy) > 1e-6:
        return {"passed": False, "key": "ch_energies_inconsistent", "params": params}
    return {"passed": True, "key": "ok", "params": params}
