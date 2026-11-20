# Molecular Hamiltonian of H₂ at 0.74 Å, STO-3G basis, Jordan-Wigner mapping
# (4 qubits). Precomputed with qml.qchem.molecular_hamiltonian(method="dhf") so
# that no chemistry is needed at run time. Exact energy: -1.1372838 Ha.
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

"""Validation for lesson 3.2: the energy of the state the circuit prepares.

Does not trust the value the learner computes: rebuilds the circuit state with
the final parameters and computes ⟨ψ|H|ψ⟩ with its own Hamiltonian.
"""

import numpy as np
import pennylane as qml

from ket_lab_engine import pl, simulator

EXACT = -1.1372838351669659
HARTREE_FOCK = -1.1167593103409306
CHEMICAL_ACCURACY = 1.6e-3


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
    # Only the chemistry ansatz: basis state (becomes X) and excitations. Preparing the
    # ground state directly (StatePrep, QubitUnitary) is not VQE.
    extra = sorted({op.name for op in ops} - {"x", "id", "singleexcitation", "doubleexcitation"})
    if extra:
        return {"passed": False, "key": "forbidden_op", "params": {"names": ", ".join(extra)}}
    state = simulator.run_ops_trajectory(ops, lines, n).states[-1]
    # The simulator uses Qiskit ordering; the PennyLane matrix uses wire 0 as the most significant bit.
    state = state.reshape((2,) * n).transpose(range(n)[::-1]).reshape(-1)
    energy = float(np.real(np.vdot(state, _hamiltonian_matrix() @ state)))
    error = energy - EXACT
    params = {"energy": energy, "error": abs(error), "exact": EXACT}
    energies = ns.get("energies") or []
    if error <= CHEMICAL_ACCURACY:
        # The convergence curve shows energies: the last value must be that of the final state.
        if not energies or abs(float(energies[-1]) - energy) > 1e-6:
            return {"passed": False, "key": "energies_inconsistent", "params": params}
        return {"passed": True, "key": "ok", "params": params}
    if abs(energy - HARTREE_FOCK) < 1e-4:
        return {"passed": False, "key": "stuck_hf", "params": params}
    if energy > HARTREE_FOCK:
        return {"passed": False, "key": "above_hf", "params": params}
    return {"passed": False, "key": "not_converged", "params": params}
