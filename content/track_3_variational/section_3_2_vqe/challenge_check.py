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

"""Challenge for lesson 3.2: what single excitations can and cannot do for H₂.

The learner fills `best_energy` with the lowest energy reachable from the Hartree–Fock state with
one qml.SingleExcitation on each pair of wires (i, j), i < j, and `gap_mha` with the distance of the
best one to the exact ground state. The check recomputes all of it: SingleExcitation acts inside the
two-dimensional space spanned by Hartree–Fock and the state with bits i and j swapped, so the best
energy of the gate is the lowest eigenvalue of H restricted to that space.
"""

import itertools

import numpy as np
import pennylane as qml

EXACT = -1.1372838351669659
TOLERANCE = 1e-4  # 0.1 mHa
GAP_TOLERANCE_MHA = 0.1
HF_BITS = (1, 1, 0, 0)


def _hamiltonian_matrix():
    ops = [qml.pauli.string_to_pauli_word(word) for _, word in H2_TERMS]
    return qml.matrix(qml.Hamiltonian([c for c, _ in H2_TERMS], ops), wire_order=range(4))


def _index(bits):
    return int("".join(str(b) for b in bits), 2)


def _best_energies():
    matrix = np.real(_hamiltonian_matrix())
    hf = _index(HF_BITS)
    best = {}
    for i, j in itertools.combinations(range(4), 2):
        bits = list(HF_BITS)
        if bits[i] == bits[j]:
            best[(i, j)] = float(matrix[hf, hf])  # the gate acts as the identity on this state
            continue
        bits[i], bits[j] = bits[j], bits[i]
        other = _index(bits)
        block = np.array([[matrix[hf, hf], matrix[hf, other]], [matrix[other, hf], matrix[other, other]]])
        best[(i, j)] = float(np.linalg.eigvalsh(block)[0])
    return best


def check(ns, run_case):
    reported = ns.get("best_energy")
    if not isinstance(reported, dict):
        return {"passed": False, "key": "ch_no_dict"}
    truth = _best_energies()
    for pair, expected in truth.items():
        if pair not in reported:
            return {"passed": False, "key": "ch_missing_pair", "params": {"pair": f"({pair[0]}, {pair[1]})"}}
        value = float(reported[pair])
        if value < expected - TOLERANCE:
            return {
                "passed": False,
                "key": "ch_too_low",
                "params": {"pair": f"({pair[0]}, {pair[1]})", "value": value, "limit": expected},
            }
        if value > expected + TOLERANCE:
            return {
                "passed": False,
                "key": "ch_not_minimized",
                "params": {"pair": f"({pair[0]}, {pair[1]})", "value": value, "best": expected},
            }
    if "gap_mha" not in ns:
        return {"passed": False, "key": "ch_no_gap"}
    gap_true = (min(truth.values()) - EXACT) * 1000
    gap = float(ns["gap_mha"])
    if abs(gap - gap_true) > GAP_TOLERANCE_MHA:
        return {"passed": False, "key": "ch_gap_wrong", "params": {"gap": gap, "gap_true": gap_true}}
    return {"passed": True, "key": "ok", "params": {"gap": gap_true, "best": min(truth.values())}}
