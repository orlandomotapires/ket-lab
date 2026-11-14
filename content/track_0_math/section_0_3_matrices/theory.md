## Matrices acting on vectors

A $2\times2$ matrix $M$ maps a vector to a vector by the usual product: the first entry of $M|\psi\rangle$ is the first row of $M$ times $|\psi\rangle$, and so on. In NumPy, `M @ psi`. The **conjugate transpose** (adjoint) $M^\dagger$ is obtained by transposing and conjugating every entry: `M.conj().T`. For example,

$$
\begin{pmatrix} 1 & i \\ 0 & 2 \end{pmatrix}^\dagger = \begin{pmatrix} 1 & 0 \\ -i & 2 \end{pmatrix}.
$$

## Unitary matrices

A matrix $U$ is **unitary** when $U^\dagger U = I$. Unitary matrices preserve inner products, $\langle U a|U b\rangle = \langle a|U^\dagger U|b\rangle = \langle a|b\rangle$, and therefore preserve norms. Every quantum gate is a unitary matrix, which is why a normalized state stays normalized.

$$
H = \frac{1}{\sqrt2}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}
$$

is unitary. $\begin{pmatrix} 1 & 1 \\ 0 & 1 \end{pmatrix}$ is not: its adjoint times itself is $\begin{pmatrix} 1 & 1 \\ 1 & 2 \end{pmatrix}$. In code, compare with `np.allclose`, because products of floating-point numbers such as $0.7071\ldots^2 \cdot 2$ are not exactly 1.

## Pauli matrices

$$
X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix},\quad
Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix},\quad
Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}.
$$

All three are unitary and equal to their own adjoint. $X$ swaps $|0\rangle$ and $|1\rangle$, and $Z$ leaves $|0\rangle$ unchanged and sends $|1\rangle$ to $-|1\rangle$.

## Eigenvalues and eigenvectors

A nonzero vector $|v\rangle$ with $M|v\rangle = \lambda|v\rangle$ is an **eigenvector** of $M$ with **eigenvalue** $\lambda$. For $Z$ the eigenvectors are $|0\rangle$ (eigenvalue $+1$) and $|1\rangle$ ($-1$). For $X$ they are $|+\rangle$ ($+1$) and $|-\rangle$ ($-1$), since $X|\pm\rangle = \pm|\pm\rangle$. The same holds for $Y$ with eigenvalues $\pm1$.

`np.linalg.eigh(M)` returns the eigenvalues in ascending order and the eigenvectors as the columns of a matrix. Each eigenvector is defined up to a phase, so the signs and phases NumPy returns can differ from the ones above.

## Hermitian matrices and expectation values

A matrix is **Hermitian** when $A^\dagger = A$. Its eigenvalues are real and eigenvectors for different eigenvalues are orthogonal. In quantum mechanics a measurable quantity (an observable) is a Hermitian matrix, and the possible measurement results are its eigenvalues. The Pauli matrices and every real symmetric matrix are Hermitian.

The **expectation value** of $A$ in the state $|\psi\rangle$ is

$$
\langle A\rangle = \langle\psi|A|\psi\rangle,
$$

the average result over many measurements of $A$ on copies of $|\psi\rangle$. It is real when $A$ is Hermitian. In NumPy, `np.vdot(psi, A @ psi)`. For $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$, $\langle Z\rangle = |\alpha|^2 - |\beta|^2$, the probability of outcome $+1$ minus the probability of outcome $-1$.
