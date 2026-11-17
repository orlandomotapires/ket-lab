## Entangling qubits that never meet

Prepare two Bell pairs, $|\Phi^+\rangle$ on qubits 0 and 1 and another on qubits 2 and 3. Qubits 0 and 3 have never been near each other: no gate has touched both. Their joint state, with the rest ignored, is a plain mixture, $I/4$, with no correlation at all. Yet a measurement on qubits 1 and 2 alone can leave 0 and 3 in a Bell state. This is **entanglement swapping**.

## Working it out

Write the two pairs as a sum over the bits $a$ of the first pair and $b$ of the second, with qubits in the order 0, 1, 2, 3 from left to right (the opposite of Qiskit's labels, chosen so that the two outer qubits can be grouped):

$$
\frac{1}{2}\sum_{a,b}|a\rangle_0|a\rangle_1|b\rangle_2|b\rangle_3 = \frac{1}{2}\sum_{a,b}|a\,b\rangle_{12}\otimes|a\,b\rangle_{03}.
$$

Now measure qubits 1 and 2 in the Bell basis, as Alice does in lesson 1.6: CNOT from qubit 1 to qubit 2, then $H$ on qubit 1, then the computational basis. Here qubit 1 plays the part of Alice's qubit 0 (its bit decides a $Z$ correction) and qubit 2 plays the part of her qubit 1 (its bit decides an $X$). The CNOT turns $|a\,b\rangle_{12}$ into $|a,\ a\oplus b\rangle$, and $H$ turns $|a\rangle$ on qubit 1 into $(|0\rangle + (-1)^a|1\rangle)/\sqrt{2}$. So if qubit 2 reads $m_2$ and qubit 1 reads $m_1$, the surviving terms are those with $a \oplus b = m_2$, each carrying the sign $(-1)^{a m_1}$.

Take $m_2 = 1$ and $m_1 = 1$. Then $b = 1 - a$, and the terms are $|a\,b\rangle_{03} = |01\rangle$ with sign $+$ and $|10\rangle$ with sign $-$, so qubits 0 and 3 are in $(|01\rangle - |10\rangle)/\sqrt{2} = |\Psi^-\rangle$. The other results give $\Phi^+$ for $m_2 m_1 = 00$, $\Phi^-$ for $01$ and $\Psi^+$ for $10$. Each of the four results has probability $1/4$.

The teleportation corrections turn every case into $|\Phi^+\rangle$ again. In the $\Psi^-$ case above, $X$ on qubit 3 (because $m_2 = 1$) gives $(|00\rangle - |11\rangle)/\sqrt{2}$ and $Z$ on qubit 3 (because $m_1 = 1$) gives $|\Phi^+\rangle$. The bits are stored by `qc.measure(1, 0)` and `qc.measure(2, 1)`, so classical bit 0 holds $m_1$ and bit 1 holds $m_2$. This pairing is the easiest thing to cross over.

## Measuring how entangled two qubits are

The validator compares the state of qubits 0 and 3 with $|\Phi^+\rangle$ using the **fidelity** $\langle\Phi^+|\rho|\Phi^+\rangle$, which is 1 when they are the same. The task also asks you to record the **concurrence** $C$ before and after. For a pure two-qubit state $\alpha|00\rangle + \beta|01\rangle + \gamma|10\rangle + \delta|11\rangle$ it equals $2|\alpha\delta - \beta\gamma|$, which is 0 for product states and 1 for Bell states. Before the measurement, though, the state of qubits 0 and 3 is the mixed state $I/4$, and for a mixed state $\rho$ one uses Wootters' general definition: take the square roots $\lambda_1 \ge \dots \ge \lambda_4$ of the eigenvalues of $\rho\,(Y\otimes Y)\rho^*(Y\otimes Y)$ and set $C = \max(0,\ \lambda_1 - \lambda_2 - \lambda_3 - \lambda_4)$. For $I/4$ this gives 0. After the measurement the state of qubits 0 and 3 is pure within one run, so both formulas agree and $C = 1$.

The library does this for you: `partial_trace(state, [1, 2])` removes qubits 1 and 2 from a state and leaves the state of 0 and 3, and `concurrence` takes it from there. `final_state(qc)` gives the final state vector of one run, with the random measurement branch fixed by its `seed` argument.
