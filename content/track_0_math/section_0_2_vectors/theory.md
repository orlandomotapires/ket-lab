## How much of a state lies along a direction

Take the state $|\psi\rangle = (0.6,\ 0.8i)$. In the computational basis the odds are $0.36$ for outcome 0 and $0.64$ for outcome 1, and that is read off the entries. Suppose instead you measure in the $\pm$ basis. The odds are not $0.36$ and $0.64$ again, and to see what they are you need the inner product.

## State vectors

A one-qubit state is a column vector in $\mathbb{C}^2$,

$$
|\psi\rangle = \begin{pmatrix} \alpha \\ \beta \end{pmatrix} = \alpha|0\rangle + \beta|1\rangle,
\qquad
|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix},\;
|1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}.
$$

Two qubits live in $\mathbb{C}^4$ with basis $|00\rangle, |01\rangle, |10\rangle, |11\rangle$, and $n$ qubits in $\mathbb{C}^{2^n}$. The symbol $|\psi\rangle$ is called a ket. Its partner $\langle\psi|$, a bra, is the same vector written as a row with every entry conjugated. In NumPy a vector is a one-dimensional array such as `np.array([1, 1j]) / np.sqrt(2)`.

## Inner product and norm

The **inner product** of $|a\rangle$ and $|b\rangle$ conjugates the entries of the first vector:

$$
\langle a|b\rangle = \sum_k a_k^*\, b_k, \qquad \langle b|a\rangle = \langle a|b\rangle^*.
$$

Take $a = (1, i)/\sqrt2$ and $b = (1, 1)/\sqrt2$. Then $\langle a|b\rangle = \tfrac12(1\cdot 1 + (-i)\cdot 1) = (1 - i)/2$, while $\langle b|a\rangle = (1 + i)/2$. The conjugation is the part that is easy to lose: `np.vdot(a, b)` includes it, and `np.dot(a, b)` leaves it out and here returns $(1+i)/2$, the answer to the other question.

The **norm** is $\|v\| = \sqrt{\langle v|v\rangle} = \sqrt{\sum_k |v_k|^2}$. A state must have norm 1, because the probabilities $|v_k|^2$ have to add up to 1. To normalize a nonzero vector, divide by its norm. For $v = (1+i,\ 1-i)$ we get $\|v\|^2 = 2 + 2 = 4$, so $\hat v = v/2$.

## Bases and the answer to the opening question

Vectors with $\langle a|b\rangle = 0$ are **orthogonal**; a set that is pairwise orthogonal with every norm equal to 1 is **orthonormal**. Two such vectors in $\mathbb{C}^2$ form a basis, and every state expands in it with coefficients $c_k = \langle e_k|\psi\rangle$. The probability of outcome $k$ is $|c_k|^2$ when the measurement is in that basis.

The $\pm$ basis is

$$
|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt2},\qquad
|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt2},
$$

and $\langle +|-\rangle = \tfrac12(1 - 1) = 0$. For $|\psi\rangle = (0.6,\ 0.8i)$,

$$
\langle +|\psi\rangle = \frac{0.6 + 0.8i}{\sqrt2},\qquad
\langle -|\psi\rangle = \frac{0.6 - 0.8i}{\sqrt2}.
$$

Both numerators have modulus $\sqrt{0.36 + 0.64} = 1$, so each outcome has probability $1/2$. The $0.6$ and $0.8$ decide the odds in the computational basis, and here it is the factor $i$ that decides them in the $\pm$ basis. The two probabilities add up to 1, as they must for any state and any orthonormal basis.
