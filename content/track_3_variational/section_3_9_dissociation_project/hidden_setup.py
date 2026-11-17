# Hidden setup for lesson 3.9: hamiltonian(d) returns the H₂ Hamiltonian (4 qubits,
# STO-3G, Jordan-Wigner, total energy in Ha) for distance d in angstrom,
# computed with qml.qchem ("dhf" method, no external dependencies; ~0.02 s).
BOHR_PER_ANGSTROM = 1.0 / 0.529177210903
hf_state = None


def _build():
    import numpy as _np
    import pennylane as _qml

    def hamiltonian(d):
        """H₂ Hamiltonian with the nuclei d angstrom apart, in the STO-3G basis."""
        coordinates = _np.array([[0.0, 0.0, 0.0], [0.0, 0.0, float(d) * BOHR_PER_ANGSTROM]])
        molecule = _qml.qchem.Molecule(["H", "H"], coordinates, basis_name="sto-3g")
        return _qml.qchem.molecular_hamiltonian(molecule, method="dhf")[0]

    return hamiltonian, _qml.numpy.array([1, 1, 0, 0], requires_grad=False)


hamiltonian, hf_state = _build()
del _build
