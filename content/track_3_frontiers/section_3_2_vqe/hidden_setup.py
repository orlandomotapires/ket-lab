# Hamiltoniano molecular do H₂ em 0,74 Å, base STO-3G, mapeamento de Jordan-Wigner
# (4 qubits). Pré-calculado com qml.qchem.molecular_hamiltonian(method="dhf") para
# não depender de química em tempo de execução. Energia exata: -1.1372838 Ha.
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


def _criar_hamiltoniano():
    import pennylane as _qml
    from pennylane import numpy as _np

    coeficientes = [c for c, _ in H2_TERMS]
    operadores = [_qml.pauli.string_to_pauli_word(palavra) for _, palavra in H2_TERMS]
    return _qml.Hamiltonian(coeficientes, operadores), _np.array([1, 1, 0, 0], requires_grad=False)


H, hf_state = _criar_hamiltoniano()
del _criar_hamiltoniano
