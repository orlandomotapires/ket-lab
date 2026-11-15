## What to build

A **dissociation curve** gives the ground-state energy $E_0(d)$ of a molecule as a function of the bond length $d$. It starts high at short distance (nuclear repulsion), has a minimum at the equilibrium bond length, and approaches the energy of the separated atoms as $d$ grows.

You compute this curve for H₂ in the STO-3G basis with VQE. The ansatz is the one of lesson 3.2: the Hartree–Fock state `hf_state = [1, 1, 0, 0]` followed by `qml.DoubleExcitation(theta)`. At each distance the Hamiltonian changes, because the integrals depend on $d$, so each point needs its own optimization. `hamiltonian(d)` builds it with `qml.qchem` (Jordan–Wigner, 4 qubits, total energy in Ha).

## Why the Hartree–Fock state is not enough

At 0.74 Å the Hartree–Fock energy is about 20 mHa above the exact one. The gap grows with $d$: at 2.0 Å it is about 165 mHa, because the exact state is a superposition of $|1100\rangle$ and $|0011\rangle$ with weights that change along the curve. The one-parameter ansatz covers every such superposition, so the optimum $\theta$ varies with $d$ while the circuit stays the same.

## Equilibrium bond length

Near the minimum the curve is close to a parabola $E \approx a d^2 + b d + c$ with $a > 0$. Fit one through the three lowest computed points; its vertex is

$$
r_{\text{eq}} = -\frac{b}{2a}.
$$

Points close to the minimum, spaced by 0.1 Å, give a better estimate. For H₂ in STO-3G the exact minimum is near 0.734 Å (the experimental value, 0.741 Å, differs because the basis is minimal).

## Rubric

The validator rebuilds each energy from your angles and compares it with the exact ground-state energy (diagonalization of the Hamiltonian). It checks five independent criteria and reports the first that fails.

1. `distances` has at least 5 distinct values between 0.5 and 2.0 Å, at least 3 of them between 0.5 and 1.0 Å, and `thetas`, `histories` and `energies` have one entry each.
2. Each training used at most 40 optimizer steps.
3. The energies you report equal those of the state with your angles, and none lies below the exact energy (the variational principle).
4. Every energy is within chemical accuracy, 1.6 mHa, of the exact one.
5. `r_eq` is within 0.05 Å of the exact minimum.

## In the lab

Dissociation shows the exact curve, the Hartree–Fock curve and your estimated minimum. Convergence shows the training of the last distance in `distances`.
