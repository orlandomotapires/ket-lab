## Mitigation and correction

Error **correction** encodes a qubit in many qubits and detects and fixes errors during the computation (lesson 4.2). It needs far more qubits than current devices have. Error **mitigation** runs the noisy circuit as it is, and removes the effect of the noise from the final numbers, with classical post-processing. Mitigation applies to expectation values, not to the quantum state. It adds no protection to the qubits, it usually removes only part of the bias, and it costs more shots.

## Readout mitigation

Measurement errors are classical and can be characterized. Prepare each basis state, measure, and record the frequencies. The **assignment matrix** has columns that are the measured distributions for each true state, $A_{ij} = P(\text{read } i \mid \text{true } j)$, so

$$
p_\text{meas} = A\,p_\text{true}.
$$

If $A$ is invertible, $p_\text{true} = A^{-1}p_\text{meas}$. For the matrix in this lesson,

$$
A = \begin{pmatrix} 0.95 & 0.10 \\ 0.05 & 0.90 \end{pmatrix}, \quad
p_\text{meas} = \begin{pmatrix} 0.78 \\ 0.22 \end{pmatrix}
\;\Rightarrow\;
p_\text{true} = \begin{pmatrix} 0.8 \\ 0.2 \end{pmatrix}.
$$

The measured $\langle Z\rangle = 0.78 - 0.22 = 0.56$ becomes $0.8 - 0.2 = 0.6$. With a finite number of shots, $p_\text{meas}$ fluctuates and the inverse can return negative probabilities. A constrained least-squares fit to valid distributions is used then. For $n$ qubits $A$ is $2^n\times2^n$, so devices use approximations, such as one matrix per qubit.

## Zero-noise extrapolation

Zero-noise extrapolation (ZNE) measures the observable at several noise levels and extrapolates to zero (Temme, Bravyi and Gambetta, 2017). The noise is made larger by **gate folding**: a gate $G$ is replaced by $G\,G^\dagger G$, which is the same operation in an ideal circuit and runs three gates in a noisy one. Folding every gate $k$ times scales the noise by $2k+1 = 1, 3, 5, \dots$

Measure $\langle O\rangle$ at each scale $s$, fit a model and evaluate it at $s=0$.

- **Linear**: a straight line through the points.
- **Richardson**: the polynomial through the points (degree 2 for three scales).
- **Exponential**: $\langle O\rangle(s) = a + b\,e^{-cs}$, natural for depolarizing noise.

In this lesson the circuit is $G = R_y(0.9)$ on $|0\rangle$, with depolarizing noise and amplitude damping after each gate. The exact $\langle Z\rangle$ is $\cos 0.9 \approx 0.622$. The noisy values are 0.599, 0.551 and 0.509 at scales 1, 3, 5, and a straight line extrapolates to 0.620.

## Limits

- The extrapolation model is an assumption. A model that does not match the noise leaves a residual bias.
- The extrapolated value has more statistical error than the data (about $1.2\sigma$ for a line and $2.3\sigma$ for the quadratic through three points), so more shots are needed.
- Folding makes circuits longer. If the noise at scale 5 already destroys the signal, the extrapolation fails.
- Readout mitigation does not touch gate errors, and ZNE does not undo readout errors. They are combined.
