## Cleaning the number instead of the qubits

Suppose the true state has $P(0)=0.8$ and $P(1)=0.2$, so $\langle Z\rangle = 0.6$, but the device reports $0.78$ and $0.22$ and you compute $0.56$. Part of the gap is the measurement, part is the gates that prepared the state. Error **correction** (lesson 4.2) would encode the qubit in many qubits and fix errors while the circuit runs, and it needs far more qubits than today's devices have. Error **mitigation** takes the noisy circuit as it is and removes the effect of the noise from the final numbers by classical post-processing. It applies to expectation values, not to the quantum state, it usually removes only part of the bias, and it costs more shots.

## Undoing the readout

Measurement errors are classical and can be characterized: prepare each basis state, measure, and record the frequencies. Column $j$ of the assignment matrix $A$ (lesson 5.3) is what the device reports when the true state is $j$, so $p_\text{meas} = A\,p_\text{true}$. For the matrix of this lesson,

$$
A = \begin{pmatrix} 0.95 & 0.10 \\ 0.05 & 0.90 \end{pmatrix}, \qquad
A^{-1} = \frac{1}{0.85}\begin{pmatrix} 0.90 & -0.10 \\ -0.05 & 0.95 \end{pmatrix},
$$

and applied to $p_\text{meas} = (0.78,\ 0.22)$ the first entry is $(0.90\cdot0.78 - 0.10\cdot0.22)/0.85 = 0.8$, so $p_\text{true} = (0.8,\ 0.2)$ and $\langle Z\rangle = 0.6$.

This has a catch. With finitely many shots $p_\text{meas}$ fluctuates, and the inverse can return a negative probability; the usual remedy is a least-squares fit restricted to valid distributions. And for $n$ qubits $A$ is $2^n\times2^n$, so real devices use approximations such as one small matrix per qubit.

## Making the noise louder, then extrapolating to zero

Gate errors cannot be inverted, but they can be amplified on purpose. Replace every gate $G$ by $G\,G^\dagger G$: in an ideal circuit it is the same operation, since $G^\dagger G$ is the identity, and on a noisy device it runs three gates, so the noise is about three times as large. Folding each gate $k$ times gives noise scales $2k+1 = 1, 3, 5,\dots$. Measure $\langle O\rangle$ at each scale, fit a curve, and read it at scale 0. This is zero-noise extrapolation (ZNE; Temme, Bravyi and Gambetta, 2017).

In this lesson $G = R_y(0.9)$ acts on $|0\rangle$, with depolarizing noise and amplitude damping after each gate, and the exact value is $\cos 0.9 \approx 0.6216$. The noisy values are 0.599, 0.551 and 0.509 at scales 1, 3, 5, so the unmitigated error is 0.023. A least-squares line through the three points reaches 0.6205 at scale 0, an error of 0.001. The polynomial through the three points (Richardson extrapolation) gives 0.6253, and an exponential $a + b\,e^{-cs}$ is the natural choice when the noise is depolarizing. The model is a guess about how the noise grows, and a wrong guess leaves a bias behind.

## What it costs

The extrapolated value is a weighted sum of noisy measurements, and the weights are not small. For the line through scales 1, 3, 5 the shot noise of the result is about $1.2\sigma$, where $\sigma$ is the noise of one measurement; for the quadratic through the same three points it is about $2.3\sigma$. So a better bias is paid for with more shots, and the more flexible curve pays more. Folding also lengthens the circuit: if at scale 5 the noise has already erased the signal, the extrapolation has nothing to work with. Readout mitigation does not touch gate errors and ZNE does not undo readout errors, which is why they are used together, as in lesson 5.5.
