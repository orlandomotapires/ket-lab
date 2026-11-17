## What happens when every angle is zero

Take the chemistry ansatz of lesson 3.2 as the baseline: one angle, and a circuit that keeps the number of electrons (the number of 1s in the bit string) fixed. A hardware-efficient ansatz (Kandala et al., 2017) is the opposite. It knows nothing about H₂ and repeats a block that a device runs well: a layer of single-qubit rotations on every qubit, then CNOT gates between neighbours. The block here is

$$
U(\vec\theta) = \prod_{\ell=1}^{L}\Big[\mathrm{CNOT\ ladder}\cdot\bigotimes_{q} R_Y(\theta_{\ell,q})\Big] \cdot \bigotimes_{q}R_Y(\theta_{0,q}),
$$

with the ladder CNOT(0,1), CNOT(1,2), CNOT(2,3), $L = 3$ layers and a last rotation layer: 16 angles on 4 qubits. It starts from the Hartree–Fock state $|1100\rangle$ of lesson 3.2 (wire 0 on the left, as PennyLane writes it).

Now set every angle to 0 and see what the circuit does. The rotations vanish and the three ladders remain. Apply one to $|1100\rangle$: CNOT(0,1) flips bit 1 because bit 0 is 1, giving $|1000\rangle$, and the two other CNOTs of the ladder do nothing because their control bits are 0. The same bookkeeping on the second ladder takes $|1000\rangle$ to $|1111\rangle$, and the third ladder ends on yet another basis state, with energy $-0.531$ Ha, which is much higher than Hartree–Fock ($-1.117$ Ha). The circuit begins with the right number of electrons and the ladders move it away. Do not start the training at zero. This state is an eigenstate of $H$ (the Hamiltonian maps it to a multiple of itself), and at an eigenstate the energy is stationary under any change of the angles, so the gradient is exactly zero for all 16 angles. Plain gradient descent, or Adam, cannot move from there. Small random starting angles break the tie.

## Why real rotations are enough

The Jordan–Wigner Hamiltonian of H₂ is a real matrix, so its ground state can be taken with real amplitudes. $R_Y$ and CNOT are real matrices, so every state of this ansatz has real amplitudes. $R_Z$ rotations would only add complex phases the problem does not need, which enlarges the search for nothing. Matching the gates to the structure of the target is a cheap way to cut the search.

## Sixteen angles against one

Both ansätze reach the exact ground state of this small model, $-1.1373$ Ha, and the best energy is identical for both. The chemistry ansatz does it with one angle, but its double-excitation gate decomposes into many native gates on a device. The hardware-efficient one needs 16 angles, because it does not know that only $|1100\rangle$ and $|0011\rangle$ matter, and its circuit is shallow and made of gates the device runs. For larger molecules the chemistry ansatz grows quickly, while the generic one can lose gradient signal as the circuit gets wide and deep, the effect of lesson 3.7.

Because the ansatz does not conserve the number of electrons, it can wander into states with the wrong particle count. These have higher energy in H₂, so the minimization avoids them, but nothing in the circuit forbids them.

## Optimizing 16 angles

Plain gradient descent uses one step size for every angle. For 16 angles with different sensitivities, **Adam** fits better: it keeps a running average of each gradient and of its square, and scales each angle's step by them. A step size of 0.1 and 150 steps from small random angles reach the exact energy to within $10^{-5}$ Ha.

Before you train, work out where the three ladders send $|1100\rangle$, and what that means for a start at zero angles. Then train from the starter's small random angles and check that the final state is concentrated on $|1100\rangle$ and $|0011\rangle$.
