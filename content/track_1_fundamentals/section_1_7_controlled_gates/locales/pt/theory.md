## Portas controladas

Uma porta controlada aplica uma operação ao **alvo** apenas quando o **controle** vale $1$. A $CS$ aplica $S$ ao alvo, o que equivale a multiplicar a amplitude de $|11\rangle$ por $i$:

$$
CS = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & i \end{pmatrix}
$$

A fase está num estado de base de **dois** qubits. Com entradas de base como $|01\rangle$ ou $|10\rangle$ nada muda, e para $|11\rangle$ só uma fase global aparece; por isso o validador usa superposições, onde a fase relativa vira diferença observável.

## Como a solução funciona

O truque é mudar o que a porta enxerga. Se $a$ e $b$ são os valores dos dois qubits, depois de `qc.cx(0, 1)` o qubit 1 guarda $a \oplus b$ (a paridade). Cada $T$ soma $\pi/4$ por qubit em $1$; o $T^{\dagger}$ sobre a paridade subtrai $\pi/4$. A fase total é

$$
\frac{\pi}{4}\bigl(a + b - (a \oplus b)\bigr) = \frac{\pi}{4}\cdot 2ab = \frac{\pi}{2}\,ab
$$

que vale $\pi/2$ só para $a = b = 1$: exatamente $CS$.

## Identidades úteis

- $S = T^2$ e $Z = S^2 = T^4$: portas de fase com ângulos que se somam.
- $HZH = X$ e $HXH = Z$: a Hadamard troca os eixos $X$ e $Z$.
- $CZ = H_{\text{alvo}}\,\text{CNOT}\,H_{\text{alvo}}$: uma Hadamard no alvo antes e depois do CNOT dá o CZ. No Qiskit, `qc.h(1); qc.cx(0, 1); qc.h(1)`.
- Hadamard nos dois qubits antes e depois de um CNOT inverte seus papéis: sai um CNOT de 1 para 0.
- $\text{SWAP}$ = três CNOTs: `qc.cx(0, 1); qc.cx(1, 0); qc.cx(0, 1)`.

## Universalidade

O CNOT e as portas de um qubit formam um **conjunto universal**: com eles se constrói qualquer porta de vários qubits, tão exata quanto se queira. Decompor operações em CNOTs e portas simples, como aqui, é o que as máquinas reais fazem para executar um circuito.

## Rz controlada e CS

Na lição 1.3 vimos que $R_z(\theta)$ e $P(\theta)$ diferem só por uma fase global. Quando a porta é **controlada**, essa fase deixa de ser global: ela vira uma fase relativa e a porta passa a atuar também sobre o qubit de controle. Por isso $CS$ não é o mesmo que uma $R_z$ controlada.
