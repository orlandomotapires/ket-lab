## Beyond the poles

In the previous lesson the qubit only visited $|0\rangle$ and $|1\rangle$. The **Hadamard** gate ($H$) takes the vector to the equator of the sphere:

$$
H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle
$$

$$
H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |-\rangle
$$

In $|+\rangle$ both amplitudes equal $\frac{1}{\sqrt{2}}$, so each outcome has probability $\left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2}$. This is a **uniform superposition**.

## What measurement does

Measuring does not reveal a value that was already there. The measurement **draws** an outcome, with the probabilities given by the amplitudes, and the state becomes the drawn outcome: the vector jumps from the equator to one of the poles. This jump is the **collapse**.

That is why a qubit in $|+\rangle$ followed by a measurement is a random bit generator. The randomness does not come from our ignorance of some detail of the system: it is part of the theory.

## Statistical fluctuation

With probability $p$ for an outcome and $N$ repetitions, the expected count is $N p$, but the actual count fluctuates around it with standard deviation $\sigma = \sqrt{N p (1-p)}$. For $N = 100$ and $p = \tfrac{1}{2}$, $\sigma = 5$: seeing $56$ zeros instead of $50$ is normal. The relative fraction fluctuates like $1/\sqrt{N}$, so with more measurements the proportion gets closer to $50\%$. With three qubits, each of the $8$ outcomes has probability $\tfrac{1}{8}$, and the counts also vary from run to run.

## A different input, a different phase

The Hadamard applied to $|1\rangle$ gives $|-\rangle$, with the same $50/50$ probabilities as $|+\rangle$. The difference is only the sign of the $|1\rangle$ amplitude, which a direct measurement does not see. Lesson 1.3 deals with this phase.

## In the lab

- `QuantumCircuit(3, 3)` creates 3 qubits and 3 classical bits, where the measurement results are stored.
- With the cursor on the measurement line, the sphere shows **one** drawn outcome. Use "Draw again" to see another.
- "Simulate 1024 measurements" repeats the whole circuit 1024 times and shows the count of each outcome.
