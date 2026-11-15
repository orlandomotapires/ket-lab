## What to build

Two Bell pairs, $|\Phi^+\rangle_{01}$ and $|\Phi^+\rangle_{23}$, are prepared first. Qubits 0 and 3 are in a product state: no gate has touched both. **Entanglement swapping** makes them entangled by acting only on qubits 1 and 2.

Measure qubits 1 and 2 in the Bell basis (CNOT from 1 to 2, $H$ on qubit 1, then computational-basis measurement). This is Alice's measurement in teleportation, with qubit 2 playing the role of the second qubit of her pair. Each of the four results has probability $1/4$ and leaves qubits 0 and 3 in a Bell state:

| Measured bits (q2 q1) | State of qubits 0 and 3 |
| :-- | :-- |
| 00 | $\Phi^+$ |
| 01 | $\Phi^-$ |
| 10 | $\Psi^+$ |
| 11 | $\Psi^-$ |

Classically controlled corrections on qubit 3, the same as in lesson 1.6, map every case to $|\Phi^+\rangle$. The bits are those of `qc.measure(1, 0)` (qubit 1) and `qc.measure(2, 1)` (qubit 2): $X$ on qubit 3 corrects the bit of qubit 2, and $Z$ the bit of qubit 1.

## Concurrence

The **concurrence** $C(\rho)$ of a two-qubit state measures entanglement: $C = 0$ for separable states and $C = 1$ for Bell states. For a pure two-qubit state $\alpha|00\rangle + \beta|01\rangle + \gamma|10\rangle + \delta|11\rangle$ it equals $2|\alpha\delta - \beta\gamma|$.

Qubits 0 and 3 are part of a four-qubit state, so their state is the reduced density operator, obtained with `partial_trace(state, [1, 2])` (it removes qubits 1 and 2). `final_state(qc)` gives the state vector after one run of the circuit, with a random measurement branch fixed by its `seed` argument.

## Rubric

The validator checks five independent criteria and reports the first that fails.

1. The circuit has 4 qubits and the classical bits for the measurements.
2. No gate acts on qubits 0 and 3 together.
3. Only qubits 1 and 2 are measured.
4. In 40 sampled runs, covering all four measurement results, the state of qubits 0 and 3 has fidelity at least 0.999 with $|\Phi^+\rangle$.
5. `c_before` is 0 and `c_after` is 1 (tolerance 0.05).

Qubit ordering: the platform follows Qiskit, so qubit 0 is the rightmost label in a state such as $|q_3 q_2 q_1 q_0\rangle$.
