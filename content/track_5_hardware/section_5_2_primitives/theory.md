## Two questions, two primitives

A quantum computation ends with a question about the final state. Qiskit has one primitive for each of the two usual questions.

- The **Sampler** answers "which bitstrings come out, and how often?". It measures in the computational basis and returns the counts (or the quasi-probability distribution) of $N$ shots.
- The **Estimator** answers "what is the expectation value $\langle\psi|O|\psi\rangle$ of an observable $O$?". It returns a number, without the learner designing the measurement.

An observable is built as a weighted sum of Pauli strings, for example `SparsePauliOp("ZZ")` or `SparsePauliOp.from_list([("ZZ", 0.5), ("XI", -1.2)])`. The Pauli string follows the Qiskit order: the rightmost character acts on qubit 0.

## PUBs

Both primitives take a list of **PUBs** (primitive unified blocks). A PUB for the Estimator is `(circuit, observables, parameter_values)`, and for the Sampler `(circuit, parameter_values)`. The last item is optional. `estimator.run([pub1, pub2])` runs both and returns one result per PUB.

```python
estimator = StatevectorEstimator()
evs = estimator.run([(qc, SparsePauliOp("ZZ"))]).result()[0].data.evs
```

`StatevectorEstimator` and `StatevectorSampler` simulate the ideal state vector, which is what the platform uses. On a device the same code uses the IBM Runtime primitives, and the circuit is first transpiled (lesson 5.1).

## Measuring a Pauli observable with counts

A measurement in the computational basis gives the eigenvalue $+1$ or $-1$ of $Z$ on each qubit. For $Z\otimes Z$ the eigenvalue of an outcome is $(-1)^{b_0+b_1}$, so

$$
\langle Z\otimes Z\rangle = \frac{1}{N}\sum_{\text{shots}} (-1)^{b_0+b_1} = P(\text{equal bits}) - P(\text{different bits}).
$$

To measure $X$, rotate it into $Z$ first: $H X H = Z$. Apply a Hadamard gate to each qubit, measure, and use the same rule. The Estimator does this basis change internally, for every Pauli term.

For the Bell state $|\Phi^+\rangle$ the exact values are $\langle ZZ\rangle = 1$, $\langle XX\rangle = 1$ and $\langle Z\otimes I\rangle = 0$. Measuring $Z$ alone on qubit 0 gives 0 and 1 with equal probability.

## Statistical error

With $N$ shots the average of $\pm1$ outcomes has standard deviation

$$
\sigma = \sqrt{\frac{1-\langle O\rangle^2}{N}} \le \frac{1}{\sqrt{N}}.
$$

For $\langle O\rangle=0$ the error is exactly $1/\sqrt N$: 0.016 for 4096 shots. Halving the error costs four times the shots. For $\langle ZZ\rangle=1$ on the Bell state every shot gives $+1$, so $\sigma=0$.

The real Estimator takes a target `precision` and chooses the number of shots itself. On the ideal `StatevectorEstimator` the default precision is 0, which returns the exact value.
