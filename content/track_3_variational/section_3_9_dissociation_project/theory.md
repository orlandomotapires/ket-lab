## How far apart do two hydrogen atoms sit?

The H₂ energy of lesson 3.2 was for one distance, 0.74 Å. Change the distance and the answer changes: push the atoms close and the nuclei repel, pull them apart and the molecule falls toward two separate atoms. In between there is a minimum, the equilibrium bond length, and the curve $E_0(d)$ that traces it is the **dissociation curve**. The project is to compute that curve with VQE and read the minimum off it.

The ansatz is the one of lesson 3.2: the Hartree–Fock state `hf_state = [1, 1, 0, 0]` followed by `qml.DoubleExcitation(theta)`. What changes with $d$ is the Hamiltonian, because the integrals that build it depend on the distance, so each point needs its own optimization. `hamiltonian(d)` builds it with `qml.qchem` (Jordan–Wigner, 4 qubits, total energy in Ha).

## Hartree–Fock gets worse as the atoms separate

At 0.74 Å the Hartree–Fock energy is 20.5 mHa above the exact one. At 2.0 Å the gap is 164.8 mHa (−0.7838 Ha against −0.9486 Ha). The exact ground state is a superposition $\cos\frac{\theta}{2}|1100\rangle - \sin\frac{\theta}{2}|0011\rangle$ of the two determinants. At 0.74 Å the weights are 98.7% and 1.3%, close to Hartree–Fock. At 2.0 Å they are 71.2% and 28.8%, and as the atoms move apart toward separated atoms the weights tend to equal. One determinant puts both electrons in the same orbital, which cannot describe two separate atoms with an electron each. The one-parameter ansatz covers every such mix, so the optimal $\theta$ grows with $d$ while the circuit stays the same.

## Locating the minimum

Close to the minimum the curve is almost a parabola $E \approx a d^2 + b d + c$ with $a > 0$, whose lowest point is

$$
r_{\text{eq}} = -\frac{b}{2a}.
$$

Here is a fit with real numbers. The exact energies at 0.6, 0.7 and 0.8 Å are $-1.11629$, $-1.13619$ and $-1.13415$ Ha. The parabola through these three points has $a = 1.097$ and $b = -1.625$, so $r_{\text{eq}} = 0.7407$ Å, within 0.007 Å of the exact minimum (0.734 Å for STO-3G; the experimental 0.741 Å differs because the basis is minimal). Spacing matters: fitting 0.5, 1.0 and 1.5 Å instead gives 0.904 Å, because those points are no longer on one parabola. Keep a few distances close together around the minimum.

Each distance starts from theta = 0.0, and 40 gradient steps are enough at every distance of the range.

Plan the loop before running it: what do you expect the optimal angle to do between 0.5 and 2.0 Å, and where does the curve flatten? The exact curve and the Hartree–Fock curve, with your estimated minimum, are in the dissociation view.
