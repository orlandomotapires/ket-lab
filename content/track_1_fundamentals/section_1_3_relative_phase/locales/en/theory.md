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

## In the lab

Watch the **phase** column in the table on the right, the pointer next to each amplitude and the color of the vector. The probability bars do not move while you rotate around $Z$.
