## The electronic Hamiltonian

The energy of a molecule's electrons is the expectation value of its **Hamiltonian** $H$. Computing the ground-state energy exactly on a classical computer costs resources that grow exponentially with the number of orbitals. A quantum computer can represent the state with one qubit per spin orbital.

In the minimal STO-3G basis, H₂ has 4 spin orbitals, so 4 qubits (occupied is $|1\rangle$). The Jordan–Wigner mapping rewrites $H$ as a sum of Pauli strings:

$$
H = \sum_j c_j\, P_j, \qquad P_j \in \{I, X, Y, Z\}^{\otimes 4}
$$

In the lab, `H` is already built for the bond length 0.74 Å. It has 15 terms (one of them the identity) and includes the nuclear repulsion, so its eigenvalues are total energies.

## The variational principle

For any normalized state $|\psi\rangle$,

$$
E(\vec\theta) = \langle \psi(\vec\theta) | H | \psi(\vec\theta) \rangle \;\ge\; E_0
$$

where $E_0$ is the ground-state energy. The ansatz prepares states $|\psi(\vec\theta)\rangle$, and a classical optimizer lowers $E(\vec\theta)$; the result is an upper bound on $E_0$. This is the **variational quantum eigensolver** (VQE).

## The chemical ansatz

1. The Hartree–Fock state `hf_state = [1, 1, 0, 0]` places the two electrons in the two lowest spin orbitals. It ignores electron correlation.
2. `qml.DoubleExcitation(θ)` rotates between this state and the one where both electrons occupy the other two orbitals:

$$
\cos\tfrac{\theta}{2}\,|1100\rangle \;-\; \sin\tfrac{\theta}{2}\,|0011\rangle
$$

(PennyLane notation, wire 0 on the left). For H₂ in this basis the ground state lies in the span of these two states, so one parameter reaches the exact energy.

## Chemical accuracy

The Hartree–Fock energy is $-1.1168$ Ha and the exact ground-state energy is $-1.1373$ Ha. The difference, about 20 mHa, is large for chemistry. **Chemical accuracy** is an error of at most $1.6$ mHa (about 1 kcal/mol), the scale of typical reaction energies.

## In the lab

- Convergence: the energy at each step, with the exact value and the chemical-accuracy band.
- Dissociation: the exact and Hartree–Fock energies against the distance between the atoms, and your result at 0.74 Å.
- Q-Sphere: the two basis states the ansatz mixes.

Click Run (or press Ctrl+Enter) to train.
