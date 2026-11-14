## Where the errors come from

A device never applies the ideal circuit. Four effects matter most, and a device reports a number for each.

- **Relaxation (T1)**: an excited qubit decays to $|0\rangle$ by losing energy to its environment.
- **Dephasing (T2)**: a superposition loses its relative phase.
- **Gate errors**: every gate is slightly wrong. Two-qubit gates are the worst, with error rates of order $10^{-3}$ to $10^{-2}$.
- **Readout error**: the measurement reports 0 when the state was 1, or the reverse.

The first two act while the qubit waits, and the longer the circuit, the more of them accumulate. This is why the depth in lesson 5.1 matters.

## T1: amplitude damping

After a time $t$, the population of $|1\rangle$ decays as

$$
P_1(t) = P_1(0)\,e^{-t/T_1}.
$$

This is the amplitude damping channel (Nielsen & Chuang, §8.3.5) with $\gamma = 1-e^{-t/T_1}$, the probability that the qubit decays during $t$. Its Kraus operators are

$$
K_0 = \begin{pmatrix}1&0\\0&\sqrt{1-\gamma}\end{pmatrix}, \qquad
K_1 = \begin{pmatrix}0&\sqrt{\gamma}\\0&0\end{pmatrix}
$$

and its action on a density matrix is $\rho_{11}\to(1-\gamma)\rho_{11}$, $\rho_{01}\to\sqrt{1-\gamma}\,\rho_{01}$.

## T2: dephasing

The off-diagonal element (the coherence) of a superposition decays as

$$
|\rho_{01}(t)| = |\rho_{01}(0)|\,e^{-t/T_2}.
$$

Amplitude damping alone already gives $\sqrt{1-\gamma} = e^{-t/(2T_1)}$. Other processes, the **pure dephasing**, add to it:

$$
\frac{1}{T_2} = \frac{1}{2T_1} + \frac{1}{T_\phi}.
$$

Since $1/T_\phi \ge 0$, we have $T_2 \le 2T_1$, and the equality holds when there is no pure dephasing. Pure dephasing is the phase damping channel, which multiplies $\rho_{01}$ by $\sqrt{1-\lambda}$ and leaves the populations alone. To reproduce a given $T_2$, use $\lambda = 1-e^{-2t/T_\phi}$.

## Idle time on a state

Take $|+\rangle$ with $\rho_{01}=\tfrac12$. With $T_1 = 100\,\mu s$, $T_2 = 80\,\mu s$ and $t = 50\,\mu s$:

$$
\rho_{11} = \tfrac12 e^{-0.5} \approx 0.303, \qquad |\rho_{01}| = \tfrac12 e^{-0.625} \approx 0.267.
$$

The state drifts toward $|0\rangle$ and its Bloch vector shrinks: the state becomes mixed (compare lesson 4.1). A circuit that runs for a time comparable to $T_2$ no longer keeps the superposition.

## Readout and gate errors

Readout error is classical. It is described by an **assignment matrix** $A$ with $A_{ij} = P(\text{read } i \mid \text{true } j)$, for example

$$
A = \begin{pmatrix} 0.97 & 0.08 \\ 0.03 & 0.92 \end{pmatrix}
$$

and the measured distribution is $p_\text{meas} = A\,p_\text{true}$. Lesson 5.4 inverts it. Readout of $|1\rangle$ is typically worse than of $|0\rangle$, because the qubit can also decay while it is measured.

A gate error is modeled as a channel after the ideal gate, most often depolarizing (with probability $p$ the qubit is replaced by the maximally mixed state), plus the T1 and T2 decay during the gate time. Device noise models combine all of these.

## In the lab

The simulator here is a density-matrix simulation, as in lesson 4.1: `qml.AmplitudeDamping(gamma, wires=0)` and `qml.PhaseDamping(lam, wires=0)` are the two channels. Move the cursor across the circuit to follow the Bloch vector.
