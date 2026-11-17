## Two states that counts cannot tell apart

$|+\rangle$ and $|-\rangle$ give 0 or 1 with probability $50\%$ each. Lesson 1.2 already showed that one more Hadamard gate sends them to different outcomes, $0$ and $1$, so they are different states even though no computational-basis measurement separates them. They differ in the sign between the two terms, the **relative phase**. Writing a general equatorial state as

$$
\frac{|0\rangle + e^{i\phi}|1\rangle}{\sqrt{2}},
$$

the angle $\phi$ is the longitude on the Bloch sphere: $\phi = 0$ is $|+\rangle$ and $\phi = \pi$ is $|-\rangle$. The probabilities hide $\phi$, but later gates can read it, because the phase decides whether amplitudes add or cancel (lesson 1.4).

## Gates that turn the vector about Z

$Z$, $S$, $T$ and $R_z(\theta)$ rotate the vector around the $Z$ axis by $180°$, $90°$, $45°$ and $\theta$ respectively. They shift $\phi$ and leave the probabilities alone. Rotations about the same axis commute and their angles add, so $S = T^2$ and $Z = S^2 = T^4$.

A small case: start in $|+\rangle$, with $\phi = 0$, and apply $T$ and then $Z$. The angles add to $\pi/4 + \pi = 5\pi/4$, and the state is $(|0\rangle + e^{5i\pi/4}|1\rangle)/\sqrt{2}$. Apply $H$ to a state with this phase and you will get 0 with probability $(1+\cos\phi)/2 \approx 0.15$, not $1/2$: the phase has become visible.

The Hadamard gate exchanges the $Z$ and $X$ axes, so a $Z$ rotation sandwiched between two Hadamard gates becomes an $X$ rotation. For the half turn this reads $HZH = X$.

## Undoing a sequence

Every gate $U$ has an inverse $U^{\dagger}$ with $U^{\dagger}U = I$, and this holds for every input, which is why you can undo a sequence without knowing the state. Take a short case: apply $S$ and then $H$ to some state. To undo it you first remove the last gate, $H$, and then $S$ with $S^{\dagger}$:

$$
(HS)^{-1} = S^{\dagger}H .
$$

In general $(U_3U_2U_1)^{-1} = U_1^{\dagger}U_2^{\dagger}U_3^{\dagger}$. The usual mistake is to repeat the gates in the original order, which only works if each gate is its own inverse. $H$ and $X$ are, so they stay as they are. $S^{\dagger}$ is a quarter turn the other way, `qc.sdg(0)`, and $T^{\dagger}$ an eighth of a turn back, `qc.tdg(0)`.

## $R_z$ against the phase gate

The phase gate $P(\theta) = \mathrm{diag}(1, e^{i\theta})$ and the rotation $R_z(\theta) = \mathrm{diag}(e^{-i\theta/2}, e^{i\theta/2})$ satisfy $R_z(\theta) = e^{-i\theta/2}P(\theta)$. On an isolated qubit the factor in front is a global phase, so they act alike, and $R_z(-\theta)$ undoes $P(\theta)$ up to $e^{i\theta/2}$. The difference matters once a gate is controlled by another qubit, which lesson 1.7 shows.

## Check it in the editor

Before you run it, predict the longitude after `qc.h(0)`, `qc.t(0)`, `qc.t(0)` and `qc.s(0)` on $|0\rangle$ (two $T$ gates make an $S$, so the total is a half turn). Then look at the phase column of the amplitude table.
