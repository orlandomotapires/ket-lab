## Chemistry on a quantum computer

The properties of a molecule (how it bonds, reacts, absorbs light) come from the energy of its electrons. Computing that energy exactly costs, on a classical computer, an effort that grows exponentially with the size of the molecule. Simulating quantum systems is the most natural application of a quantum computer.

## From the Hamiltonian to qubits

The energy is given by the electrons' **Hamiltonian** $H$. In the minimal STO-3G basis, H₂ has 4 spin orbitals; each one becomes a qubit (occupied = $|1\rangle$). The **Jordan-Wigner mapping** rewrites $H$ as a sum of products of Pauli matrices:

$$
H = \sum_j c_j\, P_j, \qquad P_j \in \{I, X, Y, Z\}^{\otimes 4}
$$

In the lab, `H` is already built: it has 15 terms, computed for the equilibrium distance of 0.74 Å.

## The variational principle

For any state $|\psi\rangle$:

$$
E(\vec\theta) = \langle \psi(\vec\theta) | H | \psi(\vec\theta) \rangle \;\ge\; E_0
$$

The energy of any state is greater than or equal to that of the ground state $E_0$. So it is enough to prepare states with a parameterized circuit and minimize $E(\vec\theta)$: the lower the energy, the closer to the ground state. This is the **VQE** (*variational quantum eigensolver*).

## The chemical ansatz

1. **Hartree-Fock**: the two electrons in the two lowest-energy orbitals, `hf_state = [1, 1, 0, 0]`. It is a good approximation, but it ignores the correlation between the electrons.
2. **Double excitation**: `qml.DoubleExcitation(θ)` mixes the Hartree-Fock state with the state in which both electrons jump together to the empty orbitals:

$$
\cos\tfrac{\theta}{2}\,|1100\rangle \;-\; \sin\tfrac{\theta}{2}\,|0011\rangle
$$

(in PennyLane notation, with wire 0 on the left). For H₂ in this basis, a single parameter is enough to reach the exact energy.

## Chemical accuracy

The Hartree-Fock energy is $-1.1168$ Ha and the exact one is $-1.1373$ Ha (the total ground-state energy, in hartrees). The difference looks small, but it decides the chemistry. The standard is to get within $1.6$ mHa of the exact value (about 1 kcal/mol): **chemical accuracy**.

## In the lab

- The **Convergence** tab shows the energy at each step, with the exact-energy line and the chemical-accuracy band.
- The **Dissociation** tab shows how the energy changes with the distance between the atoms: the exact curve, the Hartree-Fock one, and your result at 0.74 Å.
- The **Q-Sphere** shows the two states the ansatz mixes.

Click **Run** (or Ctrl+Enter) to train.
