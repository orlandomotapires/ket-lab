## A qubit that waits

Prepare $|+\rangle$ on a real qubit and do nothing for 50 µs. The state you read afterwards is not $|+\rangle$: it has drifted toward $|0\rangle$ and lost part of its superposition. Four things go wrong in a device, and each one has a number the manufacturer reports. Relaxation (time constant $T_1$) is the decay of an excited qubit to $|0\rangle$ by giving energy to its surroundings. Dephasing ($T_2$) is the loss of the relative phase of a superposition. Gate errors are the small mistakes of every gate, with two-qubit gates the worst at about $10^{-3}$ to $10^{-2}$. Readout error is the measurement reporting the wrong bit. The first two act while the qubit waits, so the longer the circuit the more of them accumulate; that is the reason depth mattered in lesson 5.1.

## T1: the population decays

After a time $t$ the population of $|1\rangle$ is

$$
P_1(t) = P_1(0)\,e^{-t/T_1}.
$$

This is the amplitude damping channel (Nielsen & Chuang, §8.3.5) with $\gamma = 1-e^{-t/T_1}$, the probability that the qubit decays during $t$. Its Kraus operators are

$$
K_0 = \begin{pmatrix}1&0\\0&\sqrt{1-\gamma}\end{pmatrix}, \qquad
K_1 = \begin{pmatrix}0&\sqrt{\gamma}\\0&0\end{pmatrix},
$$

which act on the density matrix as $\rho_{11}\to(1-\gamma)\rho_{11}$ and $\rho_{01}\to\sqrt{1-\gamma}\,\rho_{01}$. Notice the second part: relaxation also eats the coherence.

## T2: the coherence decays faster

The off-diagonal element of a superposition decays as

$$
|\rho_{01}(t)| = |\rho_{01}(0)|\,e^{-t/T_2}.
$$

Amplitude damping alone already gives $\sqrt{1-\gamma} = e^{-t/(2T_1)}$. Whatever else disturbs the phase is **pure dephasing**, with its own time $T_\phi$, and the rates add:

$$
\frac{1}{T_2} = \frac{1}{2T_1} + \frac{1}{T_\phi}.
$$

A rate cannot be negative, so $T_2 \le 2T_1$, with equality when there is no pure dephasing. Pure dephasing is the phase damping channel: it multiplies $\rho_{01}$ by $\sqrt{1-\lambda}$ and leaves the populations alone, and to match a given $T_\phi$ you take $\lambda = 1-e^{-2t/T_\phi}$.

## The numbers for 50 µs

Take $T_1 = 100\,\mu s$, $T_2 = 80\,\mu s$, $t = 50\,\mu s$, and start from $|+\rangle$, where $\rho_{01}=\tfrac12$. Amplitude damping has $\gamma = 1-e^{-0.5} \approx 0.393$. The pure dephasing rate is $1/T_\phi = 1/80 - 1/200 = 0.0075\,\mu s^{-1}$, so $T_\phi \approx 133\,\mu s$ and $\lambda = 1 - e^{-0.75} \approx 0.528$. The result is

$$
\rho_{11} = \tfrac12 e^{-0.5} \approx 0.303, \qquad |\rho_{01}| = \tfrac12 e^{-0.625} \approx 0.267.
$$

The coherence went from 0.5 to 0.267 while the population of $|1\rangle$ went from 0.5 to 0.303. The Bloch vector shrank and tilted toward $|0\rangle$, so the state is now mixed (lesson 4.1), and a circuit that lasts as long as $T_2$ no longer preserves its superposition. The usual slip is to give phase damping the whole of $1/T_2$ and forget that relaxation has already taken its share of the coherence.

## Readout and gate errors

Readout error is classical and is described by an **assignment matrix** $A$ with $A_{ij} = P(\text{read } i \mid \text{true } j)$, for example

$$
A = \begin{pmatrix} 0.97 & 0.08 \\ 0.03 & 0.92 \end{pmatrix},
$$

so that the measured distribution is $p_\text{meas} = A\,p_\text{true}$; lesson 5.4 inverts it. Reading $|1\rangle$ is usually worse than reading $|0\rangle$ because the qubit can decay during the measurement.

A gate error is modeled as a channel placed after the ideal gate, most often depolarizing (with probability $p$ the qubit is replaced by the maximally mixed state), together with the T1 and T2 decay during the gate time. A device noise model is a collection of such channels. In PennyLane the two used here are `qml.AmplitudeDamping(gamma, wires=0)` and `qml.PhaseDamping(lam, wires=0)`, simulated with a density matrix as in lesson 4.1.
