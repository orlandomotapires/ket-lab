## O problema

Agora a função secreta é o produto bit a bit de $x$ com uma string secreta $s$ de $n$ bits, módulo 2:

$$
f(x) = s \cdot x = s_0x_0 \oplus s_1x_1 \oplus \dots \oplus s_{n-1}x_{n-1}
$$

Classicamente, cada consulta revela um bit de $s$ (consultando $x = 0001$, $0010$, …), então são necessárias $n$ consultas. O algoritmo de Bernstein-Vazirani recupera $s$ inteira com **uma**.

## O mesmo circuito, outra leitura

O circuito é o de Deutsch-Jozsa. Depois do oráculo, o registrador de entrada está em

$$
\frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

e esse é exatamente o estado que as Hadamards produzem a partir de $|s\rangle$:

$$
H^{\otimes n}|s\rangle = \frac{1}{\sqrt{2^n}}\sum_x (-1)^{s\cdot x}|x\rangle
$$

Como a Hadamard desfaz a si mesma ($HH = I$), a última camada de Hadamards devolve $|s\rangle$. Medir dá $s$ com certeza.

## Como o oráculo é feito

Para cada bit $s_i = 1$, o oráculo aplica uma CNOT do qubit $i$ para o auxiliar. Com o auxiliar em $|-\rangle$, cada uma dessas CNOTs devolve o sinal $(-1)^{x_i}$ ao qubit $i$: phase kickback de novo.

## No laboratório

Na aba **Amplitudes**, depois do oráculo metade dos sinais é negativa, num padrão que codifica $s$. Depois das Hadamards, toda a amplitude se concentra num único estado. Leia $s$ com o qubit 0 à direita. Na validação, o circuito é testado com várias strings secretas.
