## Gates the hardware does not have

Teleportation used CNOT and CZ as if they were given. Real devices offer CNOT and a handful of one-qubit gates, and everything else has to be built from them. Take controlled-$S$. It applies $S = \mathrm{diag}(1, i)$ to the target when the control is 1, so it multiplies the amplitude of $|11\rangle$ by $i$ and leaves the other three basis amplitudes alone:

$$
CS = \mathrm{diag}(1, 1, 1, i).
$$

On a basis state this is almost invisible, since a phase on $|11\rangle$ is a global phase when the input is exactly $|11\rangle$. Only a superposition shows that it did anything, which is why the validator feeds superpositions too.

## Building CS from CNOT and T

Call the bits of qubits 0 and 1 $a$ and $b$. We want a phase of $\pi/2$ when $a = b = 1$ and none otherwise. A $T$ gate adds $\pi/4$ to every basis state in which its qubit is 1, so $T$ on both qubits gives $\frac{\pi}{4}(a + b)$. That is too much whenever exactly one bit is set. After `qc.cx(0, 1)` qubit 1 holds the parity $a \oplus b$, and $T^{\dagger}$ on it subtracts $\pi/4$ whenever the parity is 1. Check the four inputs:

| $(a, b)$ | $a + b$ | $a \oplus b$ | phase $\frac{\pi}{4}(a + b - a \oplus b)$ |
| :-- | :-- | :-- | :-- |
| 00 | 0 | 0 | 0 |
| 01 | 1 | 1 | 0 |
| 10 | 1 | 1 | 0 |
| 11 | 2 | 0 | $\pi/2$ |

For bits, $a + b - (a \oplus b) = 2ab$, which is why this works. A second CNOT restores qubit 1 so that the amplitudes return to their own labels. The sign of $T^{\dagger}$ is the part people usually get wrong: with two $T$ gates and no $T^{\dagger}$ the phases of $|01\rangle$ and $|10\rangle$ would not vanish.

## Rewriting one gate in terms of another

The Hadamard exchanges the $X$ and $Z$ axes, so a CNOT with a Hadamard on the target before and after it becomes a CZ. Hadamards on both qubits exchange the roles of control and target:

$$
(H \otimes H)\,\mathrm{CNOT}_{0 \to 1}\,(H \otimes H) = \mathrm{CNOT}_{1 \to 0}.
$$

A SWAP is three CNOTs, `qc.cx(0, 1); qc.cx(1, 0); qc.cx(0, 1)`. CNOT together with all one-qubit gates is universal: every operation on $n$ qubits is a circuit of them, and with a finite one-qubit set such as $H$ and $T$ it can be approximated to any accuracy.

## A controlled rotation is not a controlled phase gate

$R_z(\theta)$ and $P(\theta)$ differ by the global phase $e^{-i\theta/2}$. Controlled by another qubit, that phase is applied only on the branch where the control is 1, so it is no longer global. The controlled-$R_z(\theta)$ multiplies the states with control 1 and target 0 or 1 by $e^{-i\theta/2}$ and $e^{i\theta/2}$, while the controlled-$P(\theta)$ multiplies them by $1$ and $e^{i\theta}$. Controlled-$R_z$ equals controlled-$P$ followed by $P(-\theta/2)$ on the control qubit. For $\theta = \pi/2$ the controlled-$P$ is $CS$.

## Predict, then check

Without running anything, say what $(H \otimes H)\,\mathrm{CNOT}_{0 \to 1}\,(H \otimes H)$ does to $|10\rangle$ (qubit 1 in 1, qubit 0 in 0). Then test it in the editor with your own circuit.
