# Setup oculto da lição 3.5: hamiltonian(d) devolve o Hamiltoniano do H₂ (4 qubits,
# STO-3G, Jordan-Wigner, energia total em Ha) para a distância d em angstrom,
# calculado com qml.qchem (método "dhf", sem dependências externas; ~0,02 s).
BOHR_PER_ANGSTROM = 1.0 / 0.529177210903
hf_state = None


def _criar():
    import numpy as _np
    import pennylane as _qml

    def hamiltonian(d):
        """Hamiltoniano do H₂ com os núcleos a d angstrom, na base STO-3G."""
        coordenadas = _np.array([[0.0, 0.0, 0.0], [0.0, 0.0, float(d) * BOHR_PER_ANGSTROM]])
        molecula = _qml.qchem.Molecule(["H", "H"], coordenadas, basis_name="sto-3g")
        return _qml.qchem.molecular_hamiltonian(molecula, method="dhf")[0]

    return hamiltonian, _qml.numpy.array([1, 1, 0, 0], requires_grad=False)


hamiltonian, hf_state = _criar()
del _criar
