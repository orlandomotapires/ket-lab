## Same probabilities, different states

Compare the two states created by the Hadamard:

$$
|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}
\qquad
|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}
$$

When measured, both give $0$ or $1$ with a $50\%$ chance. Even so, they are different states, on opposite sides of the equator. The difference lies in the sign between the two terms: the **relative phase**.

In general, a state on the equator is

$$
\frac{|0\rangle + e^{i\phi}|1\rangle}{\sqrt{2}}
$$

and the angle $\phi$ says where on the equator the vector is: $\phi = 0$ is $|+\rangle$ and $\phi = \pi$ is $|-\rangle$.

## Phase gates

The gates in this lesson rotate the vector around the $Z$ axis. They change $\phi$ and leave the probabilities intact:

| Gate | Rotation around Z |
| :-- | :-- |
| $Z$ | $180°$ |
| $S$ | $90°$ |
| $T$ | $45°$ |
| $R_z(\theta)$ | $\theta$, any angle |

## Why this matters

An ordinary measurement cannot see the phase. But the gates that follow can: the phase decides whether amplitudes add up or cancel. That is the subject of the next lesson.

## Undoing a sequence

Every quantum gate has an inverse: the gate that undoes its effect. For a sequence $U_3 U_2 U_1$ (applied in the order $U_1$, $U_2$, $U_3$), the inverse is the sequence of inverses **in reverse order**:

$$
(U_3 U_2 U_1)^{-1} = U_1^{\dagger}\, U_2^{\dagger}\, U_3^{\dagger}
$$

It is like undoing the steps of a job: the last one done is the first one undone. Since $H$ and $X$ are their own inverses, only $S$ and $T$ need new gates:

| Gate | Inverse | In Qiskit |
| :-- | :-- | :-- |
| $S$ ($90°$ turn) | $S^{\dagger}$ ($-90°$ turn) | `qc.sdg(0)` |
| $T$ ($45°$ turn) | $T^{\dagger}$ ($-45°$ turn) | `qc.tdg(0)` |

Undoing works for **any** input, including ones you do not know, because the identity holds for all states at once.

## Rz and the phase gate

The phase gate $P(\theta) = \mathrm{diag}(1, e^{i\theta})$ and the rotation $R_z(\theta) = \mathrm{diag}(e^{-i\theta/2}, e^{i\theta/2})$ differ only by a global phase ($R_z(\theta) = e^{-i\theta/2} P(\theta)$). For an isolated qubit they are the same gate. The difference only shows up when one of them is controlled, as we will see in lesson 1.7.

## In the lab

Watch the **phase** column in the table on the right, the pointer next to each amplitude and the color of the vector. The probability bars do not move while you rotate around $Z$.
