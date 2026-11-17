## Two electrons, four qubits

Two hydrogen atoms 0.74 Å apart, two electrons: what is the lowest energy they can have together? The exact answer is $-1.1373$ Ha. The simplest approximation, Hartree–Fock, puts each electron in its own lowest orbital and gets $-1.1168$ Ha. The 20 mHa that it misses is large for chemistry, where **chemical accuracy**, about 1.6 mHa (1 kcal/mol), is the error at which predicted reaction energies become useful. The method of this lesson closes that gap on a quantum computer.

The energy is the expectation value of the **Hamiltonian** $H$ of the electrons. In the minimal STO-3G basis, H₂ has 4 spin orbitals, one qubit each, where $|1\rangle$ means occupied. The Jordan–Wigner mapping rewrites $H$ as a sum of Pauli strings,

$$
H = \sum_j c_j\, P_j, \qquad P_j \in \{I, X, Y, Z\}^{\otimes 4},
$$

and in the lab it is already built for 0.74 Å: 15 terms, one of them the identity, including the repulsion between the nuclei, so its eigenvalues are total energies. The Hartree–Fock state is `hf_state = [1, 1, 0, 0]`: the two electrons in the two lowest spin orbitals. Bit strings are written with wire 0 on the left, as PennyLane does.

## Why a trial state can only err upward

Take any normalized state $|\psi\rangle = \sum_k c_k |E_k\rangle$ in the eigenbasis of $H$, with $H|E_k\rangle = E_k|E_k\rangle$ and $\sum_k |c_k|^2 = 1$. Then

$$
\langle\psi|H|\psi\rangle = \sum_k |c_k|^2 E_k \;\ge\; E_0 \sum_k |c_k|^2 = E_0 ,
$$

because every $E_k \ge E_0$. The energy is a weighted average of eigenvalues, and an average cannot fall below the smallest one. Equality needs all the weight on the ground state.

So a circuit that prepares $|\psi(\vec\theta)\rangle$ with a classical optimizer lowering $E(\vec\theta)$ gives, by the variational principle, an upper bound on $E_0$ that improves as the ansatz gets closer to the ground state. This is the **variational quantum eigensolver** (VQE). The quantum computer measures $E$ term by term, since $\langle H\rangle = \sum_j c_j\langle P_j\rangle$: the constant from the identity term plus 14 expectation values, each evaluated like the cost of lesson 3.1.

## An ansatz that knows the molecule

Start from Hartree–Fock and apply `qml.DoubleExcitation(θ)`, which rotates between $|1100\rangle$ and the state where both electrons sit in the two upper orbitals:

$$
\cos\tfrac{\theta}{2}\,|1100\rangle \;-\; \sin\tfrac{\theta}{2}\,|0011\rangle .
$$

The gate keeps the number of 1s, the number of electrons, fixed. For H₂ in this basis the ground state lies in the span of these two states, so a single parameter is enough to reach the exact energy.

Here are the numbers. In the basis $\{|1100\rangle, |0011\rangle\}$ the Hamiltonian restricts to

$$
\begin{pmatrix} -1.1168 & 0.1812 \\ 0.1812 & 0.4626 \end{pmatrix} \text{ Ha},
$$

with eigenvalues $E_0 = -1.1373$ Ha and $E_1 = 0.4831$ Ha. The energy of the ansatz state is then

$$
E(\theta) = E_0 + (E_1 - E_0)\,\sin^2\tfrac{\theta - \theta^*}{2}, \qquad \theta^* \approx 0.2256 .
$$

At $\theta = 0$ this gives $-1.1373 + 1.6204\sin^2(0.1128) = -1.1168$ Ha, the Hartree–Fock energy, and it reaches $E_0$ at $\theta^*$. $E(\theta)$ is a sinusoid in $\theta$, so the parameter-shift rule applies and gradient descent walks from $0$ to $\theta^*$. The optimum is a small angle, about 0.23 rad, so a step size that is too large can overshoot it.

Before you run it, predict the sign and rough size of the final $\theta$ (from the formula above), and the number of mHa that remain above the exact value once $\theta$ is within 0.05 of $\theta^*$. Compare with your run.
