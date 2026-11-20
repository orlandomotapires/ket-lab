# H₂ Hamiltonian terms (same as the hidden setup), for the independent energy computation.
H2_TERMS = [
    (-0.0970662078, 'IIII'),
    (0.171412835, 'ZIII'),
    (0.171412835, 'IZII'),
    (0.1686889846, 'ZZII'),
    (-0.2234315573, 'IIZI'),
    (0.1206252378, 'ZIZI'),
    (0.1659278524, 'IZZI'),
    (0.0453026146, 'YXXY'),
    (-0.0453026146, 'YYXX'),
    (-0.0453026146, 'XXYY'),
    (0.0453026146, 'XYYX'),
    (-0.2234315573, 'IIIZ'),
    (0.1659278524, 'ZIIZ'),
    (0.1206252378, 'IZIZ'),
    (0.1744128778, 'IIZZ'),
]

"""Validation for lesson 3.8: the state energy of a generic ansatz for H₂.

Does not trust the value the learner computes: rebuilds the state with the final
parameters and computes ⟨ψ|H|ψ⟩ with its own Hamiltonian. Accepts only rotations and
entangling gates: no chemistry excitations, which are the lesson 3.2 ansatz.
"""

import numpy as np
import pennylane as qml

from ket_lab_engine import pl, simulator

EXACT = -1.1372838351669659
HARTREE_FOCK = -1.1167593103409306
CHEMICAL_ACCURACY = 1.6e-3
ROTATIONS = {"rx", "ry", "rz"}
ALLOWED = ROTATIONS | {"x", "id", "cx", "cz", "cy", "crx", "cry", "crz", "rzz", "h"}
MAX_ANGLES = 16


def _hamiltonian_matrix():
    ops = [qml.pauli.string_to_pauli_word(word) for _, word in H2_TERMS]
    return qml.matrix(qml.Hamiltonian([c for c, _ in H2_TERMS], ops), wire_order=range(4))


def check(ns, run_case):
    circuit = ns.get("circuit")
    if circuit is None or not pl.is_qnode(circuit):
        return {"passed": False, "key": "no_circuit"}
    if "theta" not in ns:
        return {"passed": False, "key": "no_theta"}
    ops, lines, n = pl.trace_qnode(circuit, [ns["theta"]])
    if n != 4:
        return {"passed": False, "key": "wrong_qubits", "params": {"count": n}}
    extra = sorted({op.name for op in ops} - ALLOWED)
    if extra:
        return {"passed": False, "key": "forbidden_op", "params": {"names": ", ".join(extra)}}
    angles = sum(1 for op in ops if op.name in ROTATIONS)
    if angles > MAX_ANGLES:
        return {"passed": False, "key": "too_many_angles", "params": {"count": angles, "limit": MAX_ANGLES}}
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    # The simulator uses Qiskit ordering; the PennyLane matrix uses wire 0 as the most significant bit.
    state = state.reshape((2,) * n).transpose(range(n)[::-1]).reshape(-1)
    energy = float(np.real(np.vdot(state, _hamiltonian_matrix() @ state)))
    error = energy - EXACT
    params = {"energy": energy, "error": abs(error), "exact": EXACT, "count": angles}
    if error <= CHEMICAL_ACCURACY:
        energies = ns.get("energies") or []
        if not energies or abs(float(energies[-1]) - energy) > 1e-6:
            return {"passed": False, "key": "energies_inconsistent", "params": params}
        return {"passed": True, "key": "ok", "params": params}
    if not any(len(op.qubits) == 2 for op in ops):
        return {"passed": False, "key": "no_entangler", "params": params}
    if energy > HARTREE_FOCK:
        return {"passed": False, "key": "above_hf", "params": params}
    return {"passed": False, "key": "not_converged", "params": params}
