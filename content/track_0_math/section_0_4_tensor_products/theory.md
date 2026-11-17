## Two qubits, four amplitudes

Put one qubit in $|+\rangle$ and another in $|0\rangle$. The pair needs a single vector with four entries, one per outcome $00, 01, 10, 11$, and the rule that builds it from the two single-qubit vectors is the tensor product. For $|u\rangle = (u_0, u_1)$ and $|v\rangle = (v_0, v_1)$,

$$
|u\rangle\otimes|v\rangle = \begin{pmatrix} u_0 v_0 \\ u_0 v_1 \\ u_1 v_0 \\ u_1 v_1 \end{pmatrix}.
$$

Each entry is the product of one amplitude from each factor, and the first factor changes slowest. NumPy calls it `np.kron`. A register of $n$ qubits has $2^n$ entries, so three qubits need $8$. Order matters: $|0\rangle\otimes|+\rangle = (1, 1, 0, 0)/\sqrt2$ is not $|+\rangle\otimes|0\rangle = (1, 0, 1, 0)/\sqrt2$.

## Operators on one qubit of a register

An operator on one qubit has to become a $4\times4$ matrix before it can act on the pair. The **Kronecker product** of matrices places a copy of the second matrix in each block, scaled:

$$
A\otimes B = \begin{pmatrix} a_{00} B & a_{01} B \\ a_{10} B & a_{11} B \end{pmatrix},
\qquad (A\otimes B)(|u\rangle\otimes|v\rangle) = A|u\rangle\otimes B|v\rangle.
$$

A gate on one qubit is that gate in its factor and the identity $I$ in the others. In the two-factor product, X on the second factor is $I\otimes X$ and X on the first is $X\otimes I$:

$$
I\otimes X = \begin{pmatrix} X & 0 \\ 0 & X \end{pmatrix},\qquad
X\otimes I = \begin{pmatrix} 0 & I \\ I & 0 \end{pmatrix}.
$$

Worked example: apply $I\otimes X$ to $|+\rangle\otimes|0\rangle$. By the rule above the result is $|+\rangle\otimes X|0\rangle = |+\rangle\otimes|1\rangle = (0, 1, 0, 1)/\sqrt2$. Only the second factor has changed.

## Which factor is qubit 0

Qiskit labels a basis state $|q_{n-1}\ldots q_1 q_0\rangle$ with qubit 0 on the right, and stores the amplitude of a label at the index given by reading the label as a binary number. In `np.kron` this means the highest qubit comes first and qubit 0 last. The state with qubit 1 in $|1\rangle$ and qubit 0 in $|0\rangle$ is `np.kron(one, zero)`, the vector $(0, 0, 1, 0)$, which Qiskit calls `'10'`. X on qubit 0 is $I\otimes X$, and X on qubit 1 is $X\otimes I$. This is the place where mistakes happen, and a wrong order does not raise an error: it silently flips the other qubit.

Nielsen and Chuang write qubit 0 on the left, so for them X on the first qubit is $X\otimes I$. The physics is the same and only the labels differ. This platform follows Qiskit.

## Product states and entangled states

A two-qubit vector $(a_{00}, a_{01}, a_{10}, a_{11})$ is a **product state** if it equals $|u\rangle\otimes|v\rangle$ for some single-qubit states. Then $a_{00}a_{11} = u_0v_0u_1v_1 = a_{01}a_{10}$. The converse holds too: for a nonzero vector, $a_{00}a_{11} = a_{01}a_{10}$ guarantees a product state. Arranged as the $2\times2$ matrix of its amplitudes, the equality says the matrix has determinant zero, so its rows are proportional.

A state that fails the test is **entangled**. For $(|00\rangle + |11\rangle)/\sqrt2$ the two sides are $1/2$ and $0$, so no pair of single-qubit states produces it. For $\tfrac12(1, 1, -1, -1)$ both sides are $-1/4$, and indeed the vector is $|-\rangle\otimes|+\rangle$.
