## State vectors

A quantum state of one qubit is a column vector in $\mathbb{C}^2$,

$$
|\psi\rangle = \begin{pmatrix} \alpha \\ \beta \end{pmatrix} = \alpha|0\rangle + \beta|1\rangle,
\qquad
|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix},\;
|1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}.
$$

Two qubits live in $\mathbb{C}^4$ with basis $|00\rangle, |01\rangle, |10\rangle, |11\rangle$, and $n$ qubits in $\mathbb{C}^{2^n}$. In NumPy a vector is a 1-D array, for example `np.array([1, 1j]) / np.sqrt(2)`.

## Inner product and norm

The **inner product** of $|a\rangle$ and $|b\rangle$ conjugates the entries of the first vector:

$$
\langle a|b\rangle = \sum_k a_k^*\, b_k,
\qquad
\langle b|a\rangle = \langle a|b\rangle^*.
$$

`np.vdot(a, b)` computes this. `np.dot(a, b)` does not conjugate and gives a different result for complex entries.

The **norm** is $\|v\| = \sqrt{\langle v|v\rangle} = \sqrt{\sum_k |v_k|^2}$. A valid quantum state has norm 1, because the outcome probabilities $|v_k|^2$ in the computational basis must add up to 1. To **normalize** a nonzero vector, divide it by its norm: $|\hat v\rangle = |v\rangle/\|v\|$. For $v = (1+i,\, 1-i)$, $\|v\|^2 = 2 + 2 = 4$, so $\hat v = v/2$.

For states, $|\langle a|b\rangle|^2$ is the probability of finding $|a\rangle$ when $|b\rangle$ is tested against it. For $a = (1, i)/\sqrt2$ and $b = (1, 1)/\sqrt2$, $\langle a|b\rangle = (1 - i)/2$ and the probability is $1/2$.

## Orthogonality and bases

Vectors are **orthogonal** when $\langle a|b\rangle = 0$. A set of vectors that are pairwise orthogonal and each of norm 1 is **orthonormal**. In $\mathbb{C}^2$ two orthonormal vectors form a basis, and every state expands in it:

$$
|\psi\rangle = \sum_k c_k |e_k\rangle,\qquad c_k = \langle e_k|\psi\rangle.
$$

The computational basis is $\{|0\rangle, |1\rangle\}$. The $\pm$ basis is

$$
|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt2},\qquad
|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt2},
$$

and $\langle +|-\rangle = \tfrac12(1 - 1) = 0$. The coefficient $c_k = \langle e_k|\psi\rangle$ uses the conjugated basis vector, so for a state with complex entries the conjugation matters. The probabilities $|c_k|^2$ add up to 1 for any normalized $|\psi\rangle$ and any orthonormal basis.
