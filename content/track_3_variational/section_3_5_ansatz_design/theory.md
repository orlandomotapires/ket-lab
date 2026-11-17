## An ansatz with a ceiling

Suppose you want a circuit that prepares the Bell state $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt2$, and you try $R_Y(\theta_0)\otimes R_Y(\theta_1)$ with the cost $-F$, minus the fidelity with $|\Phi^+\rangle$. The **fidelity** $F = |\langle\Phi^+|\psi\rangle|^2$ is the probability of finding the state $\psi$ in $|\Phi^+\rangle$: 1 for the same state, 0 for an orthogonal one. Training stalls at $-0.5$, and no optimizer will do better. The set of states an ansatz can prepare, its **reachable set**, does not contain the target, and the best the optimizer can do is the closest point of that set.

The ansatz prepares the product state

$$
|\psi\rangle = \left(\cos\tfrac{\theta_0}{2}|0\rangle + \sin\tfrac{\theta_0}{2}|1\rangle\right) \otimes \left(\cos\tfrac{\theta_1}{2}|0\rangle + \sin\tfrac{\theta_1}{2}|1\rangle\right),
$$

whose overlap with the Bell state is $\langle\Phi^+|\psi\rangle = \cos\tfrac{\theta_0-\theta_1}{2}/\sqrt2$. The fidelity is $F = \tfrac12\cos^2\tfrac{\theta_0-\theta_1}{2} \le \tfrac12$, with the maximum at $\theta_0 = \theta_1$. A bigger step size or more steps change nothing, because the ceiling comes from the circuit and not from the training. In general, a product state has fidelity at most $\lambda_{\max}^2$ with a given pure state, where $\lambda_{\max}$ is the largest of its Schmidt coefficients, the weights $\lambda_i$ in the decomposition $|\phi\rangle = \sum_i \lambda_i |a_i\rangle|b_i\rangle$ into orthogonal product states. For $|\Phi^+\rangle$ both are $1/\sqrt2$, which is where the 1/2 comes from.

One entangling gate repairs this. $R_Y(\pi/2)$ on qubit 0 gives $|+\rangle|0\rangle$, and a CNOT turns it into $|\Phi^+\rangle$ exactly. A larger reachable set is called more **expressive**: it holds a lower minimum, at the price of more parameters to train and more gates to run with noise on hardware.

## More parameters, but how many new directions?

The number of parameters bounds the size of the reachable set but does not equal it. What counts is the number of independent directions in which the state can move: the rank of the derivatives $\partial|\psi\rangle/\partial\theta_i$ once the direction of a global phase is removed. Computing it numerically at a random point for four ansätze on two qubits gives the following. $R_Y\otimes R_Y$ has 2 parameters and 2 directions, and adding a CNOT leaves it at 2. Adding a second layer $R_Y\otimes R_Y$ after the CNOT gives 4 parameters but only 3 directions. A rotation $R_Y R_Z$ on each qubit, a CNOT, and another $R_Y R_Z$ on each qubit gives 8 parameters and 6 directions.

Both shortfalls have a reason. States with real amplitudes on two qubits form a 3-dimensional set, so the fourth $R_Y$ has nothing left to add. Two consecutive $R_Y$ gates on one qubit are worth one, since $R_Y(\theta_2)R_Y(\theta_0) = R_Y(\theta_0+\theta_2)$. A general two-qubit pure state has 6 real degrees of freedom (4 complex amplitudes, minus normalization and global phase), which the last circuit reaches. In the last circuit the order inside each $R_Y R_Z$ is $R_Z$ first, as in the written product, and on $|0\rangle$ the first $R_Z$ is only a global phase, so two of the 8 angles do nothing. Putting $R_Y$ first avoids that waste, yet it still gives 6 directions, because 6 is all that a two-qubit state has.

## Layers that suit the hardware

Entangling gates are only available between qubits that the device connects directly. A **hardware-efficient ansatz** (Kandala et al., 2017) repeats a block of single-qubit rotations on every qubit followed by entanglers between connected neighbours, so it needs no extra transpilation, and each added block enlarges the reachable set. The ansatz knows nothing about the problem, so the number of blocks is found by trying. Lesson 3.8 trains one on a molecule.

Try this in the lab. The starter code trains the product ansatz. Before you edit it, work out how many rotation angles the Bell state needs at the very least, then add rotations and an entangler until the fidelity with $|\Phi^+\rangle$ is at least 0.99, using at most four angles.
