## Amplitudes can cancel

Probabilities can only add up. Amplitudes have a sign (and a phase), so they can also **cancel**. This is interference, and it is where quantum algorithms get their advantage.

Take two Hadamards in a row. The first takes $|0\rangle$ to $|+\rangle$. The second acts on each term:

$$
H|+\rangle = \frac{H|0\rangle + H|1\rangle}{\sqrt{2}}
= \frac{(|0\rangle + |1\rangle) + (|0\rangle - |1\rangle)}{2}
= |0\rangle
$$

The two contributions to $|1\rangle$ have opposite signs and vanish: **destructive interference**. The two to $|0\rangle$ reinforce each other: **constructive interference**. The result is $HH = I$.

## The phase chooses what is cancelled

If the relative phase is flipped in the middle, the cancellation switches sides. This is how a gate that "does not change probabilities" ends up deciding the measurement outcome.

This is why the phase from the previous lesson matters: on its own it is invisible to measurement, but a Hadamard after it turns it into probability.

## Measuring in another basis

The standard measurement distinguishes $|0\rangle$ from $|1\rangle$ (the **Z basis**) and does not distinguish $|+\rangle$ from $|-\rangle$. To tell them apart, apply a Hadamard before measuring: it takes $|+\rangle$ to $|0\rangle$ and $|-\rangle$ to $|1\rangle$. This is equivalent to measuring in the **X basis**.

## In the lab

Step through the circuit with the timeline and follow the amplitude table: look at the sign of each amplitude before the last Hadamard and at what remains after it.
