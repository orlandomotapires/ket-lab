## A gradient you can compute by hand

Take $n$ qubits, one $R_Y(\theta_q)$ on each, no entangling gate, and the cost $C = \langle Z\otimes Z\otimes\cdots\otimes Z\rangle$, the product of $Z$ on every qubit. Each qubit contributes $\cos\theta_q$, so $C = \prod_q\cos\theta_q$ and the derivative with respect to $\theta_0$ is $-\sin\theta_0\prod_{q>0}\cos\theta_q$. Draw all the angles uniformly in $[0,2\pi)$. Then $\langle\sin\theta\rangle = \langle\cos\theta\rangle = 0$, so the gradient has mean zero, while $\langle\sin^2\theta\rangle = \langle\cos^2\theta\rangle = \frac12$, so its variance is

$$
\mathrm{Var}\!\left[\frac{\partial C}{\partial\theta_0}\right] = \tfrac12\cdot\left(\tfrac12\right)^{n-1} = 2^{-n}.
$$

For 2 qubits that is $0.25$, for 6 qubits $0.016$, for 20 qubits about one millionth. The cost is a product of $n$ factors that are each below 1 in magnitude, and a shift of one angle changes only one factor. A typical gradient is of size $2^{-n/2}$, and this has a price. An evaluation with $N$ shots has a statistical error of about $1/\sqrt N$, so seeing a gradient of size $2^{-n/2}$ takes on the order of $N \sim 2^n$ shots per evaluation. At 20 qubits that is about a million shots for a single derivative.

This product ansatz is too simple to train anything, but the same decay shows up in the circuits that matter. McClean et al. (2018) proved that for circuits deep enough to behave like random unitaries the gradient of any one parameter has mean zero and a variance that shrinks exponentially with the number of qubits. The landscape is flat almost everywhere, a **barren plateau**, and an optimizer that starts at a random point has no direction to follow. A reason comes from geometry: a random state is spread nearly uniformly over a space of dimension $2^n$, and in high dimension nearly every expectation value is close to its average, so moving one angle hardly changes the cost.

## What decides whether the plateau appears

Depth, the choice of cost and the starting point all matter.

Depth: a shallow circuit does not reach the random regime. The cost: Cerezo et al. (2021) show that a cost made of observables on few qubits keeps larger gradients at shallow depth, while a global cost such as $Z^{\otimes n}$ loses them. On the ansatz below, a local cost $Z_0$ gives a variance near 0.36 for 2, 4 and 6 qubits with two layers, and 0.38, 0.24 and 0.16 for those widths with $n$ layers, where the global cost falls from 0.19 to 0.02 (values from 300 samples, so each is good to about 10 to 15%). You can try the local cost in the lab by changing the returned expectation, and predict first what 6 qubits gives. Initialization: starting near the identity circuit, rather than at random angles, keeps the circuit away from the random regime.

The remedies follow from this: a shallow ansatz built from the problem's structure, as the chemistry ansatz of lesson 3.2, a cost written as a sum of few-qubit observables, a start from a good guess such as the Hartree–Fock state instead of random angles, and training a few layers at a time. None of them removes the problem for every circuit. Some structured ansätze avoid barren plateaus but turn out to be easy to simulate on a classical computer, which makes them less attractive.

## Measuring it

In the lab the ansatz repeats a layer of $R_Y$ rotations followed by a chain of CZ gates between neighbours, with as many layers as qubits, and the global cost $\langle Z^{\otimes n}\rangle$. For each width, draw random angles in $[0,2\pi)$, compute the derivative of the first angle with the parameter-shift rule $\tfrac12[C(\theta+\tfrac\pi2)-C(\theta-\tfrac\pi2)]$, and take the variance over the samples. For two qubits it comes out near 0.19, and each added qubit roughly halves it, like the $2^{-n}$ of the product case: 0.19, 0.115, 0.06, 0.03, 0.018 for 2 to 6 qubits.

With 100 samples each estimate is noisy, about 15%. That is enough to see the ratio between 6 and 2 qubits, around 0.1, but not to read off the exact rate. The chart tab plots your variances on a logarithmic axis, where a constant ratio between neighbouring qubit counts appears as a straight line; look at how close to straight yours is.
