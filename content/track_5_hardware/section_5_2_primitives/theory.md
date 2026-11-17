## From counts to a number

Prepare a Bell state, measure both qubits 4096 times, and you get something like `{'00': 2061, '11': 2035}`. In a Qiskit key the rightmost character is qubit 0, so `'10'` would mean qubit 1 read 1 and qubit 0 read 0. Nobody cares about the counts themselves; what you want is a number such as $\langle Z\otimes Z\rangle$, and the two ways Qiskit offers to get it are the two **primitives**.

The **Sampler** returns the counts: it measures in the computational basis and reports how often each bitstring appeared in $N$ shots. The **Estimator** returns the expectation value $\langle\psi|O|\psi\rangle$ of an observable $O$ directly, and chooses the measurements itself. An observable is a weighted sum of Pauli strings, `SparsePauliOp("ZZ")` or `SparsePauliOp.from_list([("ZZ", 0.5), ("XI", -1.2)])`, and a Pauli string uses the same order as the keys: its rightmost character acts on qubit 0.

## Calling them

Both primitives take a list of **PUBs** (primitive unified blocks): `(circuit, observables, parameter_values)` for the Estimator and `(circuit, parameter_values)` for the Sampler, with the last item optional. `estimator.run([pub1, pub2])` returns one result per PUB.

```python
estimator = StatevectorEstimator()
evs = estimator.run([(qc, SparsePauliOp("ZZ"))]).result()[0].data.evs
```

The `Statevector` versions simulate the ideal state, which is what the platform runs. On a device the same code goes through the IBM Runtime primitives, after the circuit has been transpiled (lesson 5.1).

## Doing the Estimator's job by hand

A computational-basis measurement gives $+1$ or $-1$ for $Z$ on each qubit, according to whether the bit is 0 or 1. For two qubits the outcome has eigenvalue $(-1)^{b_0+b_1}$ of $Z\otimes Z$, so

$$
\langle Z\otimes Z\rangle = \frac{1}{N}\sum_{\text{shots}} (-1)^{b_0+b_1} = P(\text{equal bits}) - P(\text{different bits}).
$$

With the counts above this is $(2061 + 2035)/4096 = 1$. For $Z$ on qubit 0 alone only $b_0$ counts: the outcome `'00'` gives $+1$, `'11'` gives $-1$, and the result is $(2061 - 2035)/4096 \approx 0.006$. The exact value is 0, since qubit 0 by itself is equally likely to read 0 or 1.

To measure $X$ the circuit has to change, because the Sampler only reads $Z$. Use $H X H = Z$: put a Hadamard gate on each qubit before measuring, and then apply the same rule. The Estimator does this for every term of the observable.

The slip to expect is skipping that rotation, and the Bell state hides it, because for $|\Phi^+\rangle$ both $\langle ZZ\rangle$ and $\langle XX\rangle$ are 1. Try the state $|{+}{+}\rangle$ to see the difference: $\langle XX\rangle = 1$, but Z-basis counts give $\langle ZZ\rangle = 0$.

## Statistical error

The average of $N$ results of $\pm1$ with mean $\langle O\rangle$ fluctuates with standard deviation

$$
\sigma = \sqrt{\frac{1-\langle O\rangle^2}{N}} \le \frac{1}{\sqrt{N}}.
$$

For $\langle O\rangle=0$ it reaches the maximum: $1/\sqrt{4096} \approx 0.016$, which is why the 0.006 above is a normal result. For $\langle ZZ\rangle=1$ every shot gives $+1$ and $\sigma=0$. To make the error half as large you need four times the shots.

The real Estimator takes a target `precision` and picks the number of shots itself. On the ideal `StatevectorEstimator` the default precision is 0 and the answer is exact.
