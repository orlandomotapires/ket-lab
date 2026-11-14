## Why correct errors

Real qubits make errors: the noise from the previous lesson builds up with every gate. For long computations, errors have to be detected and undone during the calculation. This seems impossible for three reasons: an unknown state cannot be copied (the no-cloning theorem), measuring the qubit destroys the superposition, and errors are continuous. Quantum error correction gets around all three.

## Redundancy without copying

Classically, repeating is enough: $0 \to 000$, and the majority wins. Quantum mechanically, $|\psi\rangle$ cannot be copied, but the basis can be entangled:

$$
\alpha|0\rangle + \beta|1\rangle \;\longrightarrow\; \alpha|000\rangle + \beta|111\rangle
$$

with two CNOTs. This is not three copies of $|\psi\rangle$: it is a single logical state spread over three qubits.

## Measuring the error, not the state

A bit flip on qubit 1 takes the state to $\alpha|010\rangle + \beta|101\rangle$. Measuring the qubits would destroy $\alpha$ and $\beta$; but the **parities** (whether two qubits are equal or different) do not depend on them. Two ancillas store the parities of qubits 0–1 and 1–2. The pair of results, the **syndrome**, points to the error:

| Syndrome (a₃ a₄) | Error | Correction |
| :-- | :-- | :-- |
| 00 | none | none |
| 10 | X on qubit 0 | X on 0 |
| 11 | X on qubit 1 | X on 1 |
| 01 | X on qubit 2 | X on 2 |

The correction can be done without measuring, using Toffoli gates controlled by the ancillas (this is the principle of deferred measurement).

## The limits of this code

- **Two flips** give the syndrome of a single flip on the remaining qubit: the code "corrects" the wrong qubit and produces a logical error.
- **Phase flips** ($Z$) do not change any parity: they go unnoticed. An analogous code in the $X$ basis corrects $Z$, and Shor's 9-qubit code combines the two and corrects any error on a single qubit.

## The threshold

If each qubit suffers a bit flip with probability $p$, the code fails only when two or three qubits err:

$$
P_{\text{success}} = 1 - 3p^2 + 2p^3
$$

For $p < \tfrac{1}{2}$ this is better than $1 - p$, the single qubit. The idea of a **threshold** below which encoding helps is what makes fault-tolerant quantum computing possible.

## In the lab

- The buttons choose the injected error. Try the ones the code does not correct.
- In the **Register** tab, with the cursor after the syndrome, the ancilla bits appear.
- In the **Bloch spheres**, follow the data qubits.
- The **Threshold** tab compares the protected qubit with the unprotected one.
