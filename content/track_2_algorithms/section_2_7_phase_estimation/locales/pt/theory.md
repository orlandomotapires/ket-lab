## O problema

Um operador unitário $U$ tem um autovetor $|\psi\rangle$ com autovalor $e^{2\pi i\theta}$:

$$
U|\psi\rangle = e^{2\pi i\theta}|\psi\rangle, \qquad 0 \le \theta < 1
$$

A **estimação de fase** descobre $\theta$. Ela é o coração do algoritmo de Shor e de muitas simulações em química.

## A ideia

Pelo phase kickback, uma $U$ controlada com o alvo em $|\psi\rangle$ devolve a fase $e^{2\pi i\theta}$ ao controle. Aplicando $U^{2^j}$ controlada pelo qubit de contagem $j$, esse qubit ganha a fase $e^{2\pi i\,2^j\theta}$. Com $t$ qubits de contagem, o registrador fica em

$$
\frac{1}{\sqrt{2^t}}\sum_{k=0}^{2^t-1} e^{2\pi i\,\theta k}\,|k\rangle
$$

que é exatamente a QFT do número $2^t\theta$. A QFT inversa devolve esse número.

## O circuito

1. Hadamard nos qubits de contagem (0, 1 e 2) e o autovetor no qubit 3.
2. Para cada qubit de contagem $j$, a potência controlada $U^{2^j}$: `apply_controlled_u(qc, j, 2**j)`.
3. A QFT inversa da lição anterior: `inverse_qft(qc, [0, 1, 2])`.
4. Medir a contagem. O valor lido $m$ dá $\theta \approx m/2^t$.

Com $t = 3$, a precisão é de $1/8$. Quando $\theta$ não é múltiplo de $1/8$, o resultado se espalha em torno do valor mais próximo; mais qubits de contagem estreitam esse pico.

## E se a entrada não for um autovetor?

Se o qubit 3 começar em $|+\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$ em vez de $|1\rangle$, a entrada é uma superposição de dois autovetores de $U$: $|0\rangle$ (autovalor $1$, ou seja, $\theta = 0$) e $|1\rangle$ (autovalor $e^{2\pi i\theta}$). A estimação de fase mede um deles ao acaso: o registrador dá $0$ ou $\theta$, com 50% cada.

## Neste laboratório

$U$ é uma porta de fase, $U = \begin{pmatrix} 1 & 0 \\ 0 & e^{2\pi i\theta} \end{pmatrix}$, cujo autovetor é $|1\rangle$. O valor de $\theta$ é secreto. Depois de medir, `run_shots(qc)` executa o circuito 1024 vezes e devolve as contagens; com elas, calcule `theta` em Python. A aba **Registrador** mostra a probabilidade de cada valor da contagem, com a fração correspondente.
