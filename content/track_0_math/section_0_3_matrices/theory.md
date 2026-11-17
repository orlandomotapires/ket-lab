## Which matrices may act on a state

A gate takes a state to a new state, and the new state must still be normalized, or its probabilities stop adding to 1. Try two candidates on $|1\rangle = (0, 1)$. The Hadamard matrix $H = \tfrac{1}{\sqrt2}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$ gives $(1, -1)/\sqrt2$, which has norm 1. The matrix $B = \begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix}$ gives $(1, 1)$, which has norm $\sqrt2$. $B$ cannot be a gate. The rest of the lesson is the vocabulary that sorts matrices like these.

## The conjugate transpose and unitarity

A matrix acts on a vector by the usual product (`M @ psi` in NumPy). Its **conjugate transpose** $M^\dagger$ is obtained by transposing the matrix and conjugating every entry (`M.conj().T`):

$$
\begin{pmatrix} 1 & i \\ 0 & 2 \end{pmatrix}^\dagger = \begin{pmatrix} 1 & 0 \\ -i & 2 \end{pmatrix}.
$$

A matrix is **unitary** if $U^\dagger U = I$. Then $\langle Ua|Ub\rangle = \langle a|U^\dagger U|b\rangle = \langle a|b\rangle$, so inner products and norms survive, and this is the property a gate needs. For $B$ above, $B^\dagger B = \begin{pmatrix} 1 & 1 \\ 1 & 2 \end{pmatrix}$, not the identity, which matches the norm that grew. In code, test unitarity with `np.allclose` and never with `==`: for $H$ the product contains entries like $0.7071\ldots^2 + 0.7071\ldots^2$ that come out as $0.9999999999999998$.

## The Pauli matrices

$$
X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix},\quad
Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix},\quad
Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}.
$$

$X$ swaps $|0\rangle$ and $|1\rangle$, and $Z$ keeps $|0\rangle$ and flips the sign of $|1\rangle$. All three are unitary and equal to their own conjugate transpose, a second property that matters next. Mixing up the signs of the two $i$ entries of $Y$ is the usual slip, and it gives $-Y$.

## Eigenvectors

A nonzero $|v\rangle$ with $M|v\rangle = \lambda|v\rangle$ is an **eigenvector** of $M$, and $\lambda$ is its **eigenvalue**. The matrix only rescales that vector. For $Z$ the eigenvectors are $|0\rangle$ ($+1$) and $|1\rangle$ ($-1$), and for $X$ they are $|+\rangle$ ($+1$) and $|-\rangle$ ($-1$), because $X|\pm\rangle = \pm|\pm\rangle$. $Y$ also has eigenvalues $\pm1$, with eigenvectors $(1, \pm i)/\sqrt2$. In NumPy, `np.linalg.eigh(M)` returns the eigenvalues in ascending order and the eigenvectors as the columns of a matrix. An eigenvector is only defined up to a phase, so the signs NumPy returns may differ from the ones above.

## Hermitian matrices and expectation values

A matrix with $A^\dagger = A$ is **Hermitian**. Its eigenvalues are real, and eigenvectors with different eigenvalues are orthogonal. Observables are Hermitian matrices, and the possible results of measuring one are its eigenvalues. The matrix $K = \begin{pmatrix} 2 & 1-i \\ 1+i & 3 \end{pmatrix}$ is Hermitian: its diagonal is real and the two off-diagonal entries are conjugates. Its eigenvalues are $1$ and $4$.

The **expectation value** of $A$ in the state $|\psi\rangle$ is $\langle A\rangle = \langle\psi|A|\psi\rangle$, the average of the results over many measurements on copies of $|\psi\rangle$. For $|\psi\rangle = (0.6,\ 0.8i)$:

$$
Z|\psi\rangle = (0.6,\ -0.8i),\qquad \langle Z\rangle = 0.36 - 0.64 = -0.28,
$$

the probability of $+1$ minus the probability of $-1$. For $Y$ we get $Y|\psi\rangle = (0.8,\ 0.6i)$ and $\langle Y\rangle = 0.6\cdot0.8 + (-0.8i)(0.6i) = 0.96$. This one needs the conjugated bra, and forgetting it changes the answer. The result is real, as it must be for a Hermitian matrix.
