"""Validation for lesson 3.5: the state the learner's ansatz prepares.

Does not trust the value the learner computes: rebuilds the state with the final
parameters and measures the fidelity with |Φ⁺⟩ = (|00⟩ + |11⟩)/√2.
"""

import numpy as np

from ket_lab_engine import pl, simulator

ROTATIONS = {"rx", "ry", "rz"}
# allowed gates: rotations, CNOT/CZ/CY, controlled rotations and the Ising ZZ
ALLOWED = ROTATIONS | {"cx", "cz", "cy", "crx", "cry", "crz", "rzz", "h"}
MAX_ANGLES = 4
TARGET_FIDELITY = 0.99


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    if "params" not in ns:
        return {"passed": False, "key": "no_params"}
    ops, lines, n = pl.trace_qnode(circuit, [ns["params"]])
    if n != 2:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    # Only rotations and entangling gates: preparing |Φ⁺⟩ directly (StatePrep, QubitUnitary) is not designing the ansatz.
    extra = sorted({op.name for op in ops} - ALLOWED)
    if extra:
        return {"passed": False, "key": "forbidden_op", "params": {"names": ", ".join(extra)}}
    angles = sum(1 for op in ops if op.name in ROTATIONS)
    if angles > MAX_ANGLES:
        return {"passed": False, "key": "too_many_angles", "params": {"count": angles, "limit": MAX_ANGLES}}
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    fidelity = float(abs(state[0] + state[3]) ** 2 / 2)
    entangling = any(len(op.qubits) == 2 for op in ops)
    params = {"fidelity": fidelity}
    if fidelity < TARGET_FIDELITY:
        if not entangling:
            return {"passed": False, "key": "no_entangler", "params": params}
        return {"passed": False, "key": "not_converged", "params": params}
    # The convergence curve shows energies: the last value must be the cost of the final state (-F).
    energies = ns.get("energies") or []
    if not energies or abs(float(energies[-1]) + fidelity) > 1e-6:
        return {"passed": False, "key": "energies_inconsistent", "params": params}
    return {"passed": True, "key": "ok", "params": {**params, "count": angles}}
