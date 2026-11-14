## O problema

Uma função $f:\{0,1\} \to \{0,1\}$ está numa caixa-preta. Há quatro possibilidades:

| $f$ | $f(0)$ | $f(1)$ | tipo |
| :-- | :-: | :-: | :-- |
| $0$ | 0 | 0 | constante |
| $1$ | 1 | 1 | constante |
| $x$ | 0 | 1 | balanceada |
| $\text{NOT } x$ | 1 | 0 | balanceada |

A pergunta não é qual é $f$, e sim: ela é **constante** ou **balanceada**? Classicamente, são necessárias duas consultas, $f(0)$ e $f(1)$. O algoritmo de Deutsch responde com **uma**.

## O oráculo

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Aqui $x$ é o qubit 0 e $y$ é o auxiliar (qubit 1). No laboratório, o oráculo é `oracle(qc)`, com conteúdo secreto.

## Por que só o paralelismo não basta

Com a entrada em $|+\rangle$ e o auxiliar em $|0\rangle$, o oráculo calcula $f$ nas duas entradas ao mesmo tempo:

$$
\frac{1}{\sqrt2}\big(|0\rangle|f(0)\rangle + |1\rangle|f(1)\rangle\big)
$$

Mas medir só destrói a superposição e devolve o valor de $f$ em uma entrada sorteada. Falta interferência.

## O algoritmo

1. Auxiliar em $|-\rangle$ e entrada em $|+\rangle$.
2. Uma consulta. Pelo phase kickback, a entrada fica em
$$
\frac{1}{\sqrt2}\big((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle\big)
$$
3. Hadamard na entrada. Se $f(0) = f(1)$, os sinais são iguais, o estado é $\pm|+\rangle$ e o Hadamard leva a $|0\rangle$. Se $f(0) \neq f(1)$, o estado é $\pm|-\rangle$ e o Hadamard leva a $|1\rangle$.

Medir o qubit 0 dá $f(0) \oplus f(1)$ com certeza.

## O que o algoritmo revela

As funções $f = x$ e $f = \text{NOT } x$ dão a **mesma** resposta ($|1\rangle$): elas diferem por um sinal global, que não é observável. O algoritmo não revela $f(0)$ nem $f(1)$, só a propriedade global $f(0) \oplus f(1)$. Trocar duas consultas por uma é possível justamente porque a pergunta é menos exigente do que "qual é $f$?".

## No laboratório

Na aba **Amplitudes**, veja o sinal que o oráculo imprime no qubit 0 e como o último Hadamard o converte em $|0\rangle$ ou $|1\rangle$. Na validação, o circuito é testado contra as quatro funções.
