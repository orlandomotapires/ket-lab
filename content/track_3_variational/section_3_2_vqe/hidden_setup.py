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


def _build_hamiltonian():
    import pennylane as _qml
    from pennylane import numpy as _np

    coefficients = [c for c, _ in H2_TERMS]
    operators = [_qml.pauli.string_to_pauli_word(word) for _, word in H2_TERMS]
    return _qml.Hamiltonian(coefficients, operators), _np.array([1, 1, 0, 0], requires_grad=False)


H, hf_state = _build_hamiltonian()
del _build_hamiltonian
