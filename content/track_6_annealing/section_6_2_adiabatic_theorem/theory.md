## One qubit, by hand

Take the easy problem first. A single qubit with $H(s) = -(1-s)X - sZ$ starts in $|+\rangle$, the ground state of $-X$, and the sweep ends at $-Z$, whose ground state is $|0\rangle$ (spin $+1$, bit 0). The eigenvalues of $H(s)$ are $\pm\sqrt{(1-s)^2 + s^2}$, so the gap between them is $2\sqrt{1 - 2s + 2s^2}$. It is 2 at both ends and smallest at $s = 1/2$, where it equals $\sqrt{2} \approx 1.414$.

Now let the parameter change as $s = t/T$ and solve the Schrödinger equation ($\hbar = 1$, as in lesson 2.10) with small steps. The probability of ending in $|0\rangle$ is 0.52 for $T = 0.5$, 0.75 for $T = 2$ and 1.000 for $T = 5$. With $T \to 0$ the Hamiltonian changes before the state can react, so the state stays $|+\rangle$ and is found in $|0\rangle$ half the time. With $T$ large enough, the state follows the instantaneous ground state. In the language of the Landau–Zener formula for a linear sweep through an avoided crossing with minimum gap $g$, the chance of jumping to the upper level is $e^{-\pi g^2/(2v)}$, with $v$ the rate at which the energy difference of the two uncoupled levels changes. A small gap or a fast sweep makes the jump likely.

## The adiabatic theorem and its condition

If the Hamiltonian changes slowly and the gap to the first excited level stays open, a system that starts in the ground state stays close to the instantaneous ground state. This is the **adiabatic theorem**. As a recipe: encode the answer in the ground state of $H_P$, start from the easy ground state of $H_B$, and sweep $H(s) = (1-s)H_B + sH_P$ with $s = t/T$. The usual rough form of "slowly" is

$$
T \gg \frac{\max_s \lvert\langle 1|\,dH/ds\,|0\rangle\rvert}{g_{\min}^2},
$$

where $|0\rangle$ and $|1\rangle$ are the instantaneous ground state and first excited state, and $g_{\min}$ is the smallest gap over the sweep. Here $dH/ds = H_P - H_B$. The condition is a sufficient estimate, not a threshold: a sweep can succeed with a shorter $T$ than it asks for.

## The three-qubit instance

Use the instance of lesson 6.1, with $H_P = \sum_i h_iZ_i + \sum_{i<j}J_{ij}Z_iZ_j$, $h = (1/3, 2/3, 1)$, $J_{01} = 1/6$, $J_{02} = 1/4$, $J_{12} = 1/2$, and $H_B = -\sum_i X_i$. Its unique ground state is $|110\rangle$ with energy $-1.25$, and two excited states sit at $-1.0833$. In Qiskit's order, qubit 0 is the rightmost factor of every Kronecker product, so $Z_0 = I\otimes I\otimes Z$.

Diagonalizing the $8\times 8$ matrix $H(s)$ on a grid of 101 values of $s$ gives the spectrum. The gap between the two lowest levels is 2 at $s = 0$, falls, and reaches its smallest value $0.1360$ at $s = 0.95$ (a finer search puts the exact minimum at $s \approx 0.951$). At $s = 1$ it is $1/6 \approx 0.167$, so the narrowest point is just before the end, not at the end. At the minimum, $|\langle 1|dH/ds|0\rangle| \approx 0.92$, and the estimate above gives $T \gg 0.92/0.136^2 \approx 50$.

The simulation tells how loose that estimate is. The probability of finding $|110\rangle$ at the end of the sweep, from 400 midpoint steps, is 0.150 for $T = 1$, 0.373 for $T = 10$, 0.719 for $T = 100$ and 0.995 for $T = 500$. For $T = 50$ it is only 0.570. So "much larger than 50" means something like ten times larger if you want the answer with probability near one. The chart tab shows the gap along the sweep with its minimum marked, and the success probability against $T$ on a logarithmic axis, where it passes one half between $T = 10$ and $T = 100$.

## What this does not tell you

For three qubits you can diagonalize the matrix and read off $g_{\min}$. For a large instance you cannot: the matrix has $2^n$ rows, and finding $g_{\min}$ is as hard as the problem you wanted to solve. For some families of hard problems the gap is known to close exponentially with the number of qubits, which makes the required $T$ exponentially long. For others it closes polynomially. Nobody can tell in advance which case a given instance is in.
