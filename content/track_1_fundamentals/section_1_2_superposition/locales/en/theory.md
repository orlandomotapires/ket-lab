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

## In the lab

- `QuantumCircuit(1, 1)` creates 1 qubit and 1 classical bit, where the measurement result is stored.
- With the cursor on the measurement line, the sphere shows **one** drawn outcome. Use "Draw again" to see another.
- "Simulate 1024 measurements" repeats the whole circuit 1024 times and shows the count of each outcome.
