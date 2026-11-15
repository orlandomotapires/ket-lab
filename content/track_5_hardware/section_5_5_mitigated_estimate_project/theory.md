## What to build

A three-qubit GHZ state $(|000\rangle+|111\rangle)/\sqrt2$ has $\langle Z_0Z_2\rangle=1$. On the device it is lower for two reasons from lesson 5.3: readout errors and depolarizing noise after each gate. This project removes both and reports how reliable the result is.

1. **Circuit.** A Hadamard gate on qubit 0 and CNOT gates 0→1 and 1→2, which respect the line connectivity.
2. **Folding.** A circuit $G$ at noise scale $s=2k+1$ is $G\,(G^\dagger G)^k$. All three gates here are self-inverse, so $G^\dagger$ is the gate list reversed.
3. **Readout mitigation.** Prepare each of the 8 basis states, measure, and fill the assignment matrix $A_{ij}=P(\text{read }i\mid\text{prepared }j)$. Then $p_\text{meas}=A\,p_\text{true}$ is solved for $p_\text{true}$ at every scale.
4. **Zero-noise extrapolation.** Collect $\langle Z_0Z_2\rangle$ at scales 1, 3, 5 and extrapolate to 0 (Temme, Bravyi, Gambetta 2017).
5. **Uncertainty.** Repeat the estimate with different seeds. The standard deviation of the results is the statistical uncertainty of one run. It exceeds the shot noise of one measurement because the inversion of $A$ and the extrapolation amplify it.

## Qubit labels

In this lesson only, count keys write qubit 0 first ("q0 q1 q2"), so bit $i$ of the key is qubit $i$. Qiskit writes qubit 0 last.

## Rubric

| Criterion | What is checked |
|---|---|
| 1 | ghz prepares the GHZ state with neighbour-only CNOT gates |
| 2 | fold gives the folded circuit for scales 1, 3, 5, 7, on two circuits |
| 3 | A matches the device readout within 0.02 |
| 4 | raw matches the noisy device within five shot-noise widths |
| 5 | the mitigated error is at most one fifth of the raw error |
| 6 | sigma is within a factor of about 3 of the scatter of an independent run of the same estimate |
