## The Hadamard gate

The Hadamard gate $H$ takes the state vector from the poles to the equator of the Bloch sphere:

$$
H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle
\qquad
H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |-\rangle
$$

In $|+\rangle$ both amplitudes equal $1/\sqrt{2}$, so each outcome has probability $|1/\sqrt{2}|^2 = 1/2$. This is an equal (uniform) superposition of $|0\rangle$ and $|1\rangle$.

## Measurement

Measuring in the computational basis returns $0$ or $1$ with the probabilities given by the squared amplitudes. Afterwards the qubit is in the state that was found, $|0\rangle$ or $|1\rangle$: the vector jumps from the equator to a pole. This is the **collapse** of the state.

Preparing $|+\rangle$ and measuring therefore gives a random bit. The randomness is a feature of the theory, not a consequence of missing information about the qubit.

## Statistical fluctuation

If an outcome has probability $p$ and the experiment is repeated $N$ times, the expected count is $Np$ and the actual count fluctuates around it with standard deviation

$$
\sigma = \sqrt{N p (1-p)}
$$

For $N = 100$ and $p = 1/2$, $\sigma = 5$, so $56$ zeros instead of $50$ is an ordinary result. The fluctuation of the fraction scales as $1/\sqrt{N}$, so the observed proportion approaches $50\%$ as $N$ grows. With three qubits each of the $8$ outcomes has probability $1/8$, and the counts also vary from run to run.

## Same probabilities, different state

$H|1\rangle = |-\rangle$ has the same $50/50$ probabilities as $|+\rangle$. The two states differ only by the sign of the $|1\rangle$ amplitude, which a measurement in the computational basis does not detect. Lesson 1.3 treats this relative phase.

## In the lab

- `QuantumCircuit(3, 3)` creates 3 qubits and 3 classical bits to store the measurement results.
- With the cursor on the measurement line, the sphere shows one drawn outcome. "Draw again" samples another.
- "Simulate 1024 measurements" runs the whole circuit 1024 times and shows the count of each outcome.
