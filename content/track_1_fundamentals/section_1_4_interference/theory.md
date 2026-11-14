## Interference

Probabilities of exclusive alternatives add. Amplitudes are complex numbers, so they can also cancel. This is **interference**, and quantum algorithms are built to use it.

Apply two Hadamard gates in a row. The first takes $|0\rangle$ to $|+\rangle$. The second acts on each term:

$$
H|+\rangle = \frac{H|0\rangle + H|1\rangle}{\sqrt{2}}
= \frac{(|0\rangle + |1\rangle) + (|0\rangle - |1\rangle)}{2}
= |0\rangle
$$

The two contributions to $|1\rangle$ have opposite signs and cancel (destructive interference). The two contributions to $|0\rangle$ have the same sign and add (constructive interference). The result is $HH = I$.

## The phase selects what cancels

If the relative phase is flipped between the two Hadamards, the cancellation moves to the other outcome: $H|-\rangle = |1\rangle$. A gate that leaves all probabilities unchanged therefore still determines the final measurement result. This is why the relative phase of lesson 1.3 matters.

## Measuring in another basis

A measurement in the computational basis (the $Z$ basis) distinguishes $|0\rangle$ from $|1\rangle$ but not $|+\rangle$ from $|-\rangle$. Applying $H$ first maps $|+\rangle \to |0\rangle$ and $|-\rangle \to |1\rangle$, so the combination of $H$ and a standard measurement distinguishes them. This is a measurement in the $X$ basis, $\{|+\rangle, |-\rangle\}$.

## Measuring in the middle

In $HH = I$ the two $|1\rangle$ terms cancel only because both amplitudes reach the second Hadamard together. If you measure between the two gates, the state collapses to $|0\rangle$ or $|1\rangle$. The second Hadamard then produces $|+\rangle$ or $|-\rangle$, and the final outcome is $0$ or $1$ with probability $50\%$ each. The measurement has removed the interference.

## Gate order

In general $AB \neq BA$. Applying $H$ and then $S$ to $|0\rangle$ gives $SH|0\rangle = |{+i}\rangle = (|0\rangle + i|1\rangle)/\sqrt{2}$. Applying $S$ and then $H$ gives $HS|0\rangle = |+\rangle$, because $S|0\rangle = |0\rangle$. Circuits and code list gates in the order they act, while the matrix product is written in the opposite order: the rightmost operator acts first.

## In the lab

Step through the circuit with the timeline and read the amplitude table: compare the signs of the amplitudes before the last Hadamard with what remains after it.
