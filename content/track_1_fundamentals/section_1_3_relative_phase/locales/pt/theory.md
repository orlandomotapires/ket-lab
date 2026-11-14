## Mesmas probabilidades, estados diferentes

Compare os dois estados criados pela Hadamard:

$$
|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}
\qquad
|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}
$$

Medidos, ambos dão $0$ ou $1$ com $50\%$ de chance. Mesmo assim são estados diferentes, em lados opostos do equador. A diferença está no sinal entre as duas parcelas: a **fase relativa**.

No caso geral, um estado do equador é

$$
\frac{|0\rangle + e^{i\phi}|1\rangle}{\sqrt{2}}
$$

e o ângulo $\phi$ diz em que ponto do equador o vetor está: $\phi = 0$ é $|+\rangle$ e $\phi = \pi$ é $|-\rangle$.

## Portas de fase

As portas desta lição giram o vetor em torno do eixo $Z$. Elas mudam $\phi$ e deixam as probabilidades intactas:

| Porta | Giro em torno de Z |
| :-- | :-- |
| $Z$ | $180°$ |
| $S$ | $90°$ |
| $T$ | $45°$ |
| $R_z(\theta)$ | $\theta$, qualquer ângulo |

## Por que isso importa

Uma medição comum não enxerga a fase. Mas as portas seguintes enxergam: é a fase que decide se as amplitudes se somam ou se cancelam. Esse é o assunto da próxima lição.

## No laboratório

Observe a coluna **fase** na tabela à direita, o ponteiro ao lado de cada amplitude e a cor do vetor. As barras de probabilidade não se mexem enquanto você gira em torno de $Z$.
