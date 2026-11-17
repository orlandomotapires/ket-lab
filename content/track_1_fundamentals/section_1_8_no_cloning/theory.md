## What copying means

A copier would take an unknown state $|\psi\rangle$ on one qubit and a blank qubit in $|0\rangle$ and return two qubits in $|\psi\rangle|\psi\rangle$:

$$U\,|\psi\rangle|0\rangle = |\psi\rangle|\psi\rangle .$$

The no-cloning theorem states that no unitary $U$ does this for every $|\psi\rangle$. A single $U$ can copy two states $|\psi\rangle$ and $|\varphi\rangle$ only if they are equal or orthogonal.

## The CNOT copier

The CNOT gate with qubit 0 as control and qubit 1 as target copies the computational basis states:

$$|0\rangle|0\rangle \mapsto |0\rangle|0\rangle, \qquad |1\rangle|0\rangle \mapsto |1\rangle|1\rangle .$$

This works because $|0\rangle$ and $|1\rangle$ are orthogonal: the circuit copies a bit, and a bit is a quantum state that is known to be one of two orthogonal states.

For $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, linearity fixes the output:

$$\mathrm{CNOT}\,(\alpha|0\rangle + \beta|1\rangle)|0\rangle = \alpha|00\rangle + \beta|11\rangle .$$

The ideal copy is

$$|\psi\rangle|\psi\rangle = \alpha^2|00\rangle + \alpha\beta|01\rangle + \alpha\beta|10\rangle + \beta^2|11\rangle .$$

These two states are equal only if $\alpha\beta = 0$, that is, for $|0\rangle$ and $|1\rangle$ up to a global phase. For $|+\rangle$ the output is the Bell state $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$, and its **fidelity** with the ideal copy, the overlap $|\langle \text{ideal}|\text{output}\rangle|^2$ (it is 1 when two pure states are the same), is

$$|\langle ++|\Phi^+\rangle|^2 = \left(\tfrac{1}{\sqrt{2}}\right)^2 = \tfrac{1}{2} .$$

The copy is wrong in a specific way. Look at one qubit and ignore the other, which gives its **reduced state**: here each qubit alone is in the **maximally mixed state**, a fair coin in every basis, because the pair is entangled. Measuring both qubits gives 00 or 11 and never 01 or 10, whereas two real copies of $|+\rangle$ would give all four outcomes.

## Proof sketch

Suppose a unitary $U$ and a fixed ancilla state $|a\rangle$ satisfy, for two states $|\psi\rangle$ and $|\varphi\rangle$,

$$U\,|\psi\rangle|0\rangle|a\rangle = |\psi\rangle|\psi\rangle|a_\psi\rangle, \qquad U\,|\varphi\rangle|0\rangle|a\rangle = |\varphi\rangle|\varphi\rangle|a_\varphi\rangle .$$

Take the inner product of the two equations. The unitary preserves inner products, so the left sides give $\langle\psi|\varphi\rangle$ and the right sides give $\langle\psi|\varphi\rangle^2\langle a_\psi|a_\varphi\rangle$:

$$\langle\psi|\varphi\rangle = \langle\psi|\varphi\rangle^2\,\langle a_\psi|a_\varphi\rangle .$$

Since $|\langle a_\psi|a_\varphi\rangle| \le 1$, this requires $|\langle\psi|\varphi\rangle| \le |\langle\psi|\varphi\rangle|^2$, so $\langle\psi|\varphi\rangle = 0$ or $|\langle\psi|\varphi\rangle| = 1$. Two states that can be copied by the same operation are orthogonal or identical, up to a global phase. Any two distinct non-orthogonal states, such as $|0\rangle$ and $|+\rangle$, cannot.

## Consequences

Measuring a qubit does not help: it gives one classical bit and changes the state. The theorem is why quantum teleportation (lesson 1.6) moves a state and does not copy it. It also underlies quantum key distribution, since an eavesdropper cannot copy the qubits in transit.

The theorem does not forbid copying a known state, which can be prepared as many times as needed, and it does not forbid correlating one basis with several qubits, as in the three-qubit bit-flip code of Track 4.

## Check it

The editor prepares $|+\rangle$ on qubit 0 with `prepare_input`. Before you place the CNOT, predict where qubit 1 will end on the Bloch sphere (the center marks the maximally mixed state), then check. The validator also runs your circuit on $|0\rangle$, $|1\rangle$ and a state with a complex phase, and requires the CNOT output for all of them, so the single CNOT is the only copier you need.
