## Making a fair coin from a qubit

A qubit that starts in $|0\rangle$ gives 0 every time you measure it. To get a fair coin you need amplitudes of equal size, $1/\sqrt{2}$ for each outcome, so that each has probability $|1/\sqrt{2}|^2 = 1/2$. The Hadamard gate $H$ makes exactly this from either basis state:

$$
H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle
\qquad
H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |-\rangle .
$$

On the Bloch sphere $H$ takes the vector from a pole to the equator. A state with both amplitudes nonzero is a **superposition** of $|0\rangle$ and $|1\rangle$; $|+\rangle$ is the equal one.

For three qubits, one $H$ on each gives $|{+}{+}{+}\rangle$, whose 8 amplitudes all equal $1/(2\sqrt{2})$. Each of the outcomes 000 to 111 then has probability $1/8$, which is the random number generator of the mission. In the counts, the label reads qubit 2 first and qubit 0 last, so `001` means that qubit 0 gave 1.

## What a measurement does to the state

After the measurement the qubit is in the state that was found, $|0\rangle$ or $|1\rangle$: the vector jumps from the equator to a pole, and this is called the **collapse**. A second measurement of the same qubit then repeats the first result.

The theory predicts probabilities and nothing finer for a single run of this circuit. Whether that randomness is fundamental or hides something is a question about how to interpret quantum mechanics. What can be said without taking sides is that no local hidden-variable model reproduces all the predictions, which lesson 1.10 shows with a game.

## How far counts stray from the expected value

If an outcome has probability $p$ and you repeat the experiment $N$ times, you expect $Np$ occurrences, with a standard deviation of

$$
\sigma = \sqrt{N p (1-p)} .
$$

For $N = 100$ and $p = 1/2$ this is $5$, so $56$ zeros is only $1.2\sigma$ away from $50$ and means nothing. For the 8-outcome generator with $N = 1024$ and $p = 1/8$ we expect $128$ per outcome with $\sigma \approx 10.6$, so counts anywhere between about 107 and 149 are ordinary. The count deviates more as $N$ grows, but the deviation of the fraction shrinks as $1/\sqrt{N}$, which is why large samples look flat.

## Same probabilities, different state

$|+\rangle$ and $|-\rangle$ give the same 50/50 counts. They differ in the sign of the $|1\rangle$ amplitude, and a computational-basis measurement does not see signs. Lesson 1.3 studies this relative phase.

Since $H^2 = I$, applying $H$ again undoes the preparation: $H|+\rangle = |0\rangle$ and $H|-\rangle = |1\rangle$. So a final $H$ before the measurement turns the invisible sign into a visible outcome. Try this before you simulate anything: prepare $|-\rangle$ with `qc.x(0)` and `qc.h(0)`, predict the counts with and without one more `qc.h(0)` before the measurement, and then compare with the simulation.
