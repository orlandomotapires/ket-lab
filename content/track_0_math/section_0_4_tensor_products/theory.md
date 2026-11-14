## Tensor product of vectors

Two qubits in the states $|u\rangle = (u_0, u_1)$ and $|v\rangle = (v_0, v_1)$ are described by the **tensor product** (Kronecker product)

$$
|u\rangle\otimes|v\rangle = \begin{pmatrix} u_0 v_0 \\ u_0 v_1 \\ u_1 v_0 \\ u_1 v_1 \end{pmatrix}.
$$

Each entry is the product of one amplitude of $u$ and one of $v$, and the first factor changes slowest. In NumPy, `np.kron(u, v)`. For example `|0⟩ ⊗ |1⟩ = (0, 1, 0, 0)`. A register of $n$ qubits has a state vector of dimension $2^n$, so `np.kron(np.kron(a, b), c)` has 8 entries. The tensor product is associative but not commutative: $|u\rangle\otimes|v\rangle \neq |v\rangle\otimes|u\rangle$ in general.

## Tensor product of matrices

For matrices, the Kronecker product places a copy of the second matrix, scaled, in each block:

$$
A\otimes B = \begin{pmatrix} a_{00} B & a_{01} B \\ a_{10} B & a_{11} B \end{pmatrix}.
$$

It satisfies $(A\otimes B)(|u\rangle\otimes|v\rangle) = A|u\rangle\otimes B|v\rangle$. A gate that acts on one qubit of a register is the Kronecker product of that gate with identity matrices $I$ on the others. With two qubits, "X on the first factor" is $X\otimes I$ and "X on the second factor" is $I\otimes X$:

$$
I\otimes X = \begin{pmatrix} X & 0 \\ 0 & X \end{pmatrix},\qquad
X\otimes I = \begin{pmatrix} 0 & I \\ I & 0 \end{pmatrix}.
$$

## Qubit ordering

Qiskit labels a basis state $|q_{n-1}\ldots q_1 q_0\rangle$ with qubit 0 on the right, and the amplitude of the label read as a binary number is stored at that index. In `np.kron`, the factor for the highest qubit comes first and the factor for qubit 0 comes last. With two qubits, the state with qubit 1 in $|1\rangle$ and qubit 0 in $|0\rangle$ is `np.kron(one, zero)`, the vector $(0, 0, 1, 0)$, and Qiskit calls it `'10'`. X on qubit 0 is $I\otimes X$ and X on qubit 1 is $X\otimes I$.

Nielsen and Chuang write qubit 0 on the left. In their convention $X$ on the first qubit is $X\otimes I$. Both conventions describe the same physics with different labels. This platform follows Qiskit.

## Product states and entangled states

A two-qubit vector $(a_{00}, a_{01}, a_{10}, a_{11})$ is a **product state** when it equals $|u\rangle\otimes|v\rangle$ for some single-qubit states. Then $a_{00}a_{11} = u_0v_0u_1v_1 = a_{01}a_{10}$. Conversely, for any nonzero vector the equality

$$
a_{00}\,a_{11} = a_{01}\,a_{10}
$$

implies that it is a product state. A state that fails the test is **entangled**. For $(|00\rangle + |11\rangle)/\sqrt2$, $a_{00}a_{11} = 1/2$ and $a_{01}a_{10} = 0$, so it is entangled: no pair of single-qubit states produces it. For $\tfrac12(1, 1, -1, -1) = |-\rangle\otimes|+\rangle$ both sides equal $-1/4$.
