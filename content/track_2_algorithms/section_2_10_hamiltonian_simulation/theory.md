## The problem

A quantum computer simulates a Hamiltonian $H$ by applying the unitary $e^{-iHt}$ to a state. For a system of many qubits, $H$ is a sum of local terms, $H = \sum_k H_k$, and each $e^{-iH_k t}$ is a gate on a few qubits. The exponential of the sum is harder to implement, because the terms usually do not commute.

If $A$ and $B$ commute, $e^{-i(A+B)t} = e^{-iAt}e^{-iBt}$. If they do not, the product differs from the exponential of the sum.

## The Trotter formula

Split the time $t$ into $n$ steps of length $\Delta t = t/n$ and apply the terms one after another in each step:

$$
e^{-i(A+B)t} \approx \left(e^{-iA\Delta t}\,e^{-iB\Delta t}\right)^n
$$

Expanding one step to second order in $\Delta t$,

$$
e^{-iA\Delta t}e^{-iB\Delta t} = e^{-i(A+B)\Delta t - \frac{1}{2}[A,B]\Delta t^2 + O(\Delta t^3)}
$$

so one step has error $O(\Delta t^2)$ and the $n$ steps accumulate $n\,O(t^2/n^2)$:

$$
\left\| e^{-i(A+B)t} - \left(e^{-iA\Delta t}e^{-iB\Delta t}\right)^n \right\| = O\!\left(\frac{t^2}{n}\right)
$$

with a constant proportional to $\|[A,B]\|$. This is the first-order formula. Doubling $n$ halves the error of the state. The infidelity $1-F$, with $F = |\langle\psi_{\text{exact}}|\psi_{\text{approx}}\rangle|^2$, is quadratic in that error and falls by a factor of 4.

The symmetric (second-order) formula uses the step $e^{-iA\Delta t/2}e^{-iB\Delta t}e^{-iA\Delta t/2}$, whose error is $O(t^3/n^2)$. Each step costs one more gate, but halving the error takes a factor $\sqrt 2$ more steps instead of 2.

## The Hamiltonian of this lesson

For two qubits take

$$
H = J\,Z\otimes Z + h\,(X\otimes I + I\otimes X)
$$

The terms $Z\otimes Z$ and $X\otimes I$ anticommute on the first qubit, so the formula is not exact. The parts of one step are:

- $e^{-iJ\,Z\otimes Z\,\Delta t}$, which is `qc.rzz(2*J*dt, 0, 1)`, since $R_{ZZ}(\theta) = e^{-i\theta\, Z\otimes Z/2}$;
- $e^{-ih\,X\,\Delta t}$ on each qubit, which is `qc.rx(2*h*dt, q)`, since $R_x(\theta) = e^{-i\theta X/2}$.

The terms $X\otimes I$ and $I\otimes X$ commute, so they can be applied in either order within a step without adding error.

## In the lab

Start from $|00\rangle$ and compare the final state for $n=1$ with larger $n$. The amplitudes approach those of $e^{-iHt}|00\rangle$ as $n$ grows. The validator computes this exact state with a matrix exponential of $H$ and requires fidelity at least 0.99. For $J=1$, $h=0.8$ and $t=2$ the fidelity is about 0.42 for $n=1$ and passes 0.99 once $n$ is large enough; try several values.

## Qubit ordering

Qiskit writes qubit 0 on the right of the label, $|q_1 q_0\rangle$. The Hamiltonian is symmetric under swapping the two qubits, so the ordering does not change the result of this lesson.
