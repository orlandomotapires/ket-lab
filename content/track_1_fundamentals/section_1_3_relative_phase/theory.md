## Relative phase

The states

$$
|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}
\qquad
|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}
$$

both give $0$ or $1$ with probability $50\%$ in the computational basis, yet they are different states, on opposite sides of the equator. They differ in the sign between the two terms, the **relative phase**.

A general equatorial state is

$$
\frac{|0\rangle + e^{i\phi}|1\rangle}{\sqrt{2}}
$$

where the angle $\phi$ is the longitude of the vector on the equator: $\phi = 0$ is $|+\rangle$ and $\phi = \pi$ is $|-\rangle$.

A measurement in the computational basis cannot see $\phi$, but later gates can: the phase decides whether amplitudes add or cancel (lesson 1.4).

## Phase gates

These gates rotate the vector around the $Z$ axis. They change $\phi$ and leave the probabilities unchanged:

| Gate | Rotation around Z |
| :-- | :-- |
| $Z$ | $180°$ |
| $S$ | $90°$ |
| $T$ | $45°$ |
| $R_z(\theta)$ | $\theta$, any angle |

Rotations about the same axis commute and their angles add: $S = T^2$, $Z = S^2$.

## Undoing a sequence

Every gate $U$ is unitary, so it has an inverse $U^{\dagger}$ that undoes it. For a sequence applied in the order $U_1$, $U_2$, $U_3$, the inverse is the product of inverses in reverse order:

$$
(U_3 U_2 U_1)^{-1} = U_1^{\dagger}\, U_2^{\dagger}\, U_3^{\dagger}
$$

The last gate applied is the first one undone. $H$ and $X$ are their own inverses, so only $S$ and $T$ need new gates:

| Gate | Inverse | In Qiskit |
| :-- | :-- | :-- |
| $S$ ($90°$ rotation) | $S^{\dagger}$ ($-90°$) | `qc.sdg(0)` |
| $T$ ($45°$ rotation) | $T^{\dagger}$ ($-45°$) | `qc.tdg(0)` |

The identity $U^{\dagger}U = I$ holds for every state, so the sequence is undone even when the input state is unknown.

## $R_z$ and the phase gate

The phase gate $P(\theta) = \mathrm{diag}(1, e^{i\theta})$ and the rotation $R_z(\theta) = \mathrm{diag}(e^{-i\theta/2}, e^{i\theta/2})$ are related by $R_z(\theta) = e^{-i\theta/2} P(\theta)$. They differ only by a global phase, so on an isolated qubit they act identically. The difference appears when the gate is controlled (lesson 1.7).

## In the lab

The table on the right lists the phase of each amplitude; the vector color follows it. The probability bars do not change under rotations about $Z$.
