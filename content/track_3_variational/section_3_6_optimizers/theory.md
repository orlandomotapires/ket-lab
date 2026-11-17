## The bill for a gradient

On hardware, one evaluation of a cost means running the circuit for thousands of shots, so the number of evaluations is what you pay for, more than the number of optimizer steps. Gradient descent with the parameter-shift rule of lesson 3.1 needs two evaluations for every parameter, and it needs them at every step. With $P$ parameters one step costs $2P$ evaluations, and a run of $T$ steps costs $2PT$. The ansatz of this lesson has $P = 4$ angles, so a step costs 8 evaluations, plus one if you also want to record the cost. For $P = 40$ it is 80 per step, and the bill grows with the size of the circuit you want to train.

The rule gives the gradient exactly, so what is left is shot noise. If the evaluations are the problem, a cheaper and noisier gradient may be the better trade.

## SPSA: one random direction

**Simultaneous perturbation stochastic approximation** (Spall, 1992) moves all parameters at once. Draw a vector $\vec\Delta$ with entries $\pm1$ and estimate

$$
\hat g_k = \frac{C(\vec\theta + c\vec\Delta) - C(\vec\theta - c\vec\Delta)}{2c\,\Delta_k}.
$$

Two evaluations give the slope of the cost along $\vec\Delta$, whatever $P$ is, and since $\Delta_k = \pm 1$ the estimate for each parameter is that slope multiplied by $\Delta_k$. Averaged over the random $\vec\Delta$, it points along the true gradient. The gain sequences shrink with the step number $k$, $a_k = a/k^{0.602}$ and $c_k = c/k^{0.101}$: large early steps explore, small late steps settle, and the perturbation $c_k$ falls slowly so that shot noise does not swamp the difference of the two evaluations.

Take one real step. The cost is the minus fidelity of lesson 3.5, with angles $(0.4, 1.2, 0.3, 0.8)$ and cost $-0.347$. In step 1 the gains are $a_1 = 0.6$ and $c_1 = 0.2$, and the random signs came out as $\vec\Delta = (+,+,+,+)$. The two evaluations at $\vec\theta \pm 0.2\vec\Delta$ give $-0.3377$ and $-0.3401$, so the slope along $\vec\Delta$ is $(-0.3377 + 0.3401)/0.4 = 0.0061$. Each angle then moves by $-0.6 \cdot 0.0061 \cdot \Delta_k = -0.0037$, and the cost goes from $-0.34732$ to $-0.34734$, almost nothing. That is not an error: the true gradient at that point is $(-0.33, 0.34, -0.28, 0.28)$, and a direction of all plus signs is almost perpendicular to it (its slope along $\vec\Delta$ is the sum, $0.006$). One draw of $\vec\Delta$ can be a bad guess.

Step 2 has $a_2 = 0.395$, $c_2 = 0.186$ and $\vec\Delta = (+,+,+,-)$, which has a large overlap with the gradient. The evaluations give $-0.4326$ and $-0.2380$, a slope of $-0.52$, and the angles move by $+0.206\,\Delta_k$ to $(0.603, 1.403, 0.503, 0.590)$, with cost $-0.4388$. Over many steps the good guesses outweigh the bad ones, and with the seed of the lab the cost reaches $-0.99$ after 60 steps.

## COBYLA: no gradient at all

**COBYLA** (constrained optimization by linear approximation) builds a linear model of the cost from $P+1$ recent evaluations and moves within a trust region that shrinks as the model improves. It needs no gradient and no random numbers, spends one evaluation per step, and is a common default for small variational problems. The number of steps it needs tends to grow with $P$. Parameter-shift descent suits few parameters and an exact simulator, SPSA suits many parameters and noisy hardware, COBYLA suits small problems with a smooth cost.

In the lab, finish with SPSA on the four angles, using no more than 200 evaluations in total, counting the one that you spend recording the cost at each step. Before you write it, work out how many steps that allows and how many the parameter-shift rule would allow. The chart tab plots the cost after each step from your `energies` list, with the minimum of −1 as a dashed line, so you can see how quickly the path gets close to it and how uneven it is on the way.
