## From a Hamiltonian to a circuit

A system with Hamiltonian $H$ (its energy operator) evolves for a time $t$ by the unitary $e^{-iHt}$, in units with $\hbar = 1$. The exponential of a matrix is defined by the same power series as for numbers, $e^{M} = I + M + M^2/2! + \dots$. For a single Pauli term it is easy: since $X^2 = I$, $e^{-ihXt} = \cos(ht)\,I - i\sin(ht)\,X$, which is the rotation $R_x(2ht)$. The same works for $Z\otimes Z$ and the gate $R_{ZZ}$.

A many-qubit $H$ is a sum of such local terms, $H = \sum_k H_k$, and each $e^{-iH_kt}$ is a small gate. The trouble is that the exponential of a sum is not the product of the exponentials. If $A$ and $B$ commute, $e^{-i(A+B)t} = e^{-iAt}e^{-iBt}$. If not, it fails. The **commutator** $[A,B] = AB - BA$ measures this, and it is zero exactly when the matrices commute. For $X$ and $Z$ it is $XZ - ZX = -2iY$, not zero.

A small case: one qubit with $H = X + Z$, starting in $|0\rangle$, for $t = 1$. The product $e^{-iXt}e^{-iZt}$ applied once has fidelity 0.594 with the exact $e^{-iHt}|0\rangle$.

## Trotter steps

The fix is to cut the time into $n$ steps of length $\Delta t = t/n$ and apply the terms one after another in each step:

$$
e^{-i(A+B)t} \approx \left(e^{-iA\Delta t}\,e^{-iB\Delta t}\right)^n
$$

In the one-qubit case, 4 steps give fidelity 0.9825 and 8 steps give 0.9959. To second order in $\Delta t$,

$$
e^{-iA\Delta t}e^{-iB\Delta t} = e^{-i(A+B)\Delta t - \frac{1}{2}[A,B]\Delta t^2 + O(\Delta t^3)}
$$

so one step has error $O(\Delta t^2)$ and $n$ steps accumulate $n\,O(t^2/n^2)$:

$$
\left\| e^{-i(A+B)t} - \left(e^{-iA\Delta t}e^{-iB\Delta t}\right)^n \right\| = O\!\left(\frac{t^2}{n}\right)
$$

with a constant proportional to $\|[A,B]\|$. Doubling $n$ halves the error of the state. The infidelity $1 - F$, with $F = |\langle\psi_{\text{exact}}|\psi_{\text{approx}}\rangle|^2$, is quadratic in that error, so it falls by about a factor of 4.

The symmetric formula, with the step $e^{-iA\Delta t/2}e^{-iB\Delta t}e^{-iA\Delta t/2}$, has error $O(t^3/n^2)$. Neighboring half steps merge into one gate, so each step costs about the same as before.

## The model of this lesson

For two qubits take

$$
H = J\,Z\otimes Z + h\,(X\otimes I + I\otimes X)
$$

This is the transverse-field Ising model: two spins coupled along $z$ with strength $J$, in a field $h$ along $x$, across the coupling direction. $Z\otimes Z$ and $X\otimes I$ do not commute, so Trotter steps are needed. In one step apply $e^{-iJ\,Z\otimes Z\,\Delta t}$, which is `qc.rzz(2*J*dt, 0, 1)` because $R_{ZZ}(\theta) = e^{-i\theta\, Z\otimes Z/2}$, then $e^{-ihX\Delta t}$ on each qubit, which is `qc.rx(2*h*dt, q)`. The two $X$ terms commute with each other, so their order inside a step costs nothing.

With $J = 1$, $h = 0.8$, $t = 2$ and start $|00\rangle$, one step gives fidelity 0.417. Seven steps give 0.9895, just below 0.99, and eight steps pass.
