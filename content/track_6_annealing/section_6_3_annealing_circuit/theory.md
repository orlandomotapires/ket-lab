## An anneal on a gate-based machine

The three spins of lessons 6.1 and 6.2 have a unique lowest-energy state, $s = (+1,-1,-1)$, which is $x = (0,1,1)$ and the basis state $|110\rangle$ in Qiskit's label (a spin $s = +1$ is $|0\rangle$, and qubit 0 is the rightmost). Its energy is $-1.25$; the next two states sit at $-1.083$, only 0.167 above. The adiabatic picture of lesson 6.2 says to start in the ground state $|{+}{+}{+}\rangle$ of $H_B = -\sum_i X_i$ and let

$$
H(s) = (1-s)\,H_B + s\,H_P, \qquad s = t/T,
$$

run slowly from $s=0$ to $s=1$, with $H_P = \sum_i h_i Z_i + \sum_{i<j} J_{ij} Z_i Z_j$ and $\hbar = 1$. An annealer does this with a continuous drive. A circuit has no such drive, so we cut it.

## Trotter steps with a frozen schedule

Split $[0,T]$ into $p$ steps of length $\Delta t = T/p$. In step $k$ freeze the schedule at its midpoint, $s_k = (k-\tfrac12)/p$, and apply the two exponentials one after the other, as in lesson 2.10:

$$
U_k = e^{-i(1-s_k)\,\Delta t\,H_B}\; e^{-i s_k\,\Delta t\,H_P}.
$$

The cost layer is a set of commuting rotations. Qiskit's gates are $R_Z(\theta) = e^{-i\theta Z/2}$ and $R_{ZZ}(\theta) = e^{-i\theta ZZ/2}$, so a coefficient $c$ acting for a time $\tau$ needs the angle $2c\tau$: `rz(2*s*h[i]*dt)` on qubit $i$ and `rzz(2*s*J[i,j]*dt)` on each pair. The mixer has the sign that people lose. Since $H_B = -\sum X_i$,

$$
e^{-i(1-s_k)\Delta t\,H_B} = e^{+i(1-s_k)\Delta t\,X}, \qquad\text{so the gate is } R_X\bigl(-2(1-s_k)\Delta t\bigr).
$$

One step by hand: take $T = 10$, $p = 5$, so $\Delta t = 2$, and $k = 1$, so $s_1 = 0.1$. The angles are rz: $0.1333,\ 0.2667,\ 0.4$ on qubits 0, 1, 2; rzz: $0.0667$ on (0,1), $0.1$ on (0,2), $0.2$ on (1,2); rx: $-3.6$ on every qubit. Check one amplitude. The state $|110\rangle$ has $E = -1.25$, so the cost layer multiplies it by $e^{-i\,0.1\cdot 2\cdot(-1.25)} = e^{+0.25i}$. Adding the gate phases one by one (each rz contributes $\mp\theta/2$, each rzz contributes $\mp\theta/2$ by parity) gives $-0.0667+0.1333+0.2+0.0333+0.05-0.1 = 0.25$, as expected. After the mixer of that first step the probability of $|110\rangle$ has moved from $0.125$ to $0.090$: at $s = 0.1$ the state should still look like $|{+}{+}{+}\rangle$.

## How long is long enough

Numbers from the simulation of this circuit, with $s_k$ at the midpoint. At $T = p = 10$ the probability of $|110\rangle$ is 0.384, at $T = p = 30$ it is 0.494, at $T = p = 100$ it is 0.722, and the exact continuous evolution needs $T = 300$ for 0.96. The reason is the gap: the smallest gap of $H(s)$ is 0.136, near $s = 0.95$, and the adiabatic theorem asks for a time that grows as the gap shrinks. The step matters too. At $T = 120$, $p = 100$ ($\Delta t = 1.2$) the probability is 0.768; at the same $T$ with $p = 60$ it collapses to 0.013, because a step that long is no longer a good Trotter approximation. Both knobs have to be right, and the angles above are where a wrong factor shows: with the cost angles halved, $T = 120$, $p = 100$ gives only 0.513, and with the mixer sign flipped the state ends on $|000\rangle$, the highest-energy state, with probability 1.000.

## Next to QAOA

The circuit has exactly the shape of QAOA (lesson 3.3): a cost layer, then a mixer layer, $p$ times, starting from $|{+}{+}{+}\rangle$. The mixer here is $e^{+i\beta\sum X}$, which in lesson 3.3 is the same thing with $\beta \to -\beta$. What differs is where the angles come from. The anneal takes them from a fixed schedule, $\gamma_k = s_k\Delta t$ and $\beta_k = (1-s_k)\Delta t$, and needs about a hundred layers. QAOA treats them as free parameters and trains them. On this instance the best angles for 1, 2, 3 and 4 layers give 0.383, 0.706, 0.888 and 0.980 on $|110\rangle$, with 12 to 39 gates, against 0.77 for the 900-gate anneal. With many layers QAOA can reproduce the anneal, so it is never worse in the limit; with few layers, trained angles are usually much better.

## Next to thermal annealing

Simulated annealing (Kirkpatrick, Gelatt and Vecchi) is a classical algorithm: flip a random spin, accept the flip if it lowers the energy, and accept an increase with probability $e^{-\Delta E/k_BT}$, lowering the temperature $T$ over time. It crosses an energy barrier by climbing over it with a thermal fluctuation. Quantum annealing, as proposed by Kadowaki and Nishimori, crosses it by tunnelling, driven by the transverse field. Which one is faster depends on the landscape: tall, thin barriers favour tunnelling, wide ones favour thermal climbing. For general problems no advantage of the quantum version has been established, and this three-qubit example, which a computer solves by trying eight states, says nothing about that.
