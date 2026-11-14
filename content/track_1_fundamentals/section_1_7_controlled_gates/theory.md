## Controlled operations

A controlled operation applies a gate to the **target** qubit only when the **control** qubit is $1$. Controlled-$S$ ($CS$) applies $S = \mathrm{diag}(1, i)$ to the target, which multiplies the amplitude of $|11\rangle$ by $i$:

$$
CS = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & i \end{pmatrix}
$$

The phase acts on a basis state of two qubits. On $|00\rangle$, $|01\rangle$ and $|10\rangle$ the gate does nothing, and on $|11\rangle$ it only adds a global phase. Only a superposition shows the relative phase, so the validator tests superpositions as well.

## Building CS from CNOT and T

Let $a$ and $b$ be the values of qubits 0 and 1. After `qc.cx(0, 1)`, qubit 1 holds the parity $a \oplus b$. Each $T$ adds $\pi/4$ for every qubit that is $1$, and $T^{\dagger}$ on the parity subtracts $\pi/4$ when $a \oplus b = 1$. The total phase is

$$
\frac{\pi}{4}\bigl(a + b - (a \oplus b)\bigr) = \frac{\pi}{4}\cdot 2ab = \frac{\pi}{2}\,ab
$$

because $a + b - (a \oplus b) = 2ab$ for bits. This equals $\pi/2$ only when $a = b = 1$, which is $CS$. A second CNOT restores qubit 1.

## Identities between gates

- $S = T^2$ and $Z = S^2 = T^4$: phase gates whose angles add.
- $HZH = X$ and $HXH = Z$: the Hadamard exchanges the $X$ and $Z$ axes.
- $CZ = H_{\text{target}}\,\text{CNOT}\,H_{\text{target}}$: a Hadamard on the target before and after the CNOT. In Qiskit, `qc.h(1); qc.cx(0, 1); qc.h(1)`.
- $(H \otimes H)\,\text{CNOT}_{0 \to 1}\,(H \otimes H) = \text{CNOT}_{1 \to 0}$: Hadamards on both qubits exchange control and target.
- $\text{SWAP}$ is three CNOTs: `qc.cx(0, 1); qc.cx(1, 0); qc.cx(0, 1)`.

## Universality

CNOT together with single-qubit gates is a **universal** set: any unitary operation on $n$ qubits can be written as a circuit of these gates. With a finite single-qubit set such as $H$ and $T$, any such operation can be approximated to arbitrary accuracy. Hardware executes circuits by decomposing them into gates of this kind.

## Controlled $R_z$ and $CS$

$R_z(\theta)$ and $P(\theta)$ differ by the global phase $e^{-i\theta/2}$. In a controlled gate this phase becomes a relative phase between the control states $0$ and $1$, so it acts on the control qubit. Controlled-$R_z(\theta)$ is $\mathrm{diag}(1, 1, e^{-i\theta/2}, e^{i\theta/2})$, which is not controlled-$P(\theta)$. For $\theta = \pi/2$, $CS$ is controlled-$P(\pi/2)$.
