"""Challenge for lesson 3.5: |Φ⁺⟩ with a single rotation angle.

Same cost and same fidelity measurement as the mission, but at most ONE rotation angle, no Hadamard
(it would prepare the superposition with no angle at all) and a stricter fidelity of 0.999.
"""

import numpy as np

from ket_lab_engine import pl, simulator

ROTATIONS = {"rx", "ry", "rz"}
ALLOWED = ROTATIONS | {"cx", "cz", "cy"}
MAX_ANGLES = 1
TARGET_FIDELITY = 0.999


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "ch_no_circuit"}
    if "params" not in ns:
        return {"passed": False, "key": "ch_no_params"}
    ops, lines, n = pl.trace_qnode(circuit, [ns["params"]])
    if n != 2:
        return {"passed": False, "key": "ch_wrong_qubits", "params": {"count": n}}
    extra = sorted({op.name for op in ops} - ALLOWED)
    if extra:
        return {"passed": False, "key": "ch_forbidden_op", "params": {"names": ", ".join(extra)}}
    angles = sum(1 for op in ops if op.name in ROTATIONS)
    if angles > MAX_ANGLES:
        return {"passed": False, "key": "ch_too_many_angles", "params": {"count": angles, "limit": MAX_ANGLES}}
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    fidelity = float(abs(state[0] + state[3]) ** 2 / 2)
    params = {"fidelity": fidelity}
    if fidelity < TARGET_FIDELITY:
        if not any(len(op.qubits) == 2 for op in ops):
            return {"passed": False, "key": "ch_no_entangler", "params": params}
        return {"passed": False, "key": "ch_not_converged", "params": {**params, "target": TARGET_FIDELITY}}
    energies = ns.get("energies") or []
    if not energies or abs(float(energies[-1]) + fidelity) > 1e-6:
        return {"passed": False, "key": "ch_energies_inconsistent", "params": params}
    return {"passed": True, "key": "ok", "params": {**params, "count": angles}}
