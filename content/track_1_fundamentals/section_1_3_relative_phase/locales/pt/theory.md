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

## Desfazer uma sequência

Toda porta quântica tem inverso: a porta que desfaz o seu efeito. Para uma sequência $U_3 U_2 U_1$ (aplicada na ordem $U_1$, $U_2$, $U_3$), o inverso é a sequência dos inversos **na ordem contrária**:

$$
(U_3 U_2 U_1)^{-1} = U_1^{\dagger}\, U_2^{\dagger}\, U_3^{\dagger}
$$

É como desfazer as etapas de um trabalho: a última a ser feita é a primeira a ser desfeita. Como $H$ e $X$ são os próprios inversos, só $S$ e $T$ precisam de portas novas:

| Porta | Inverso | No Qiskit |
| :-- | :-- | :-- |
| $S$ (giro de $90°$) | $S^{\dagger}$ (giro de $-90°$) | `qc.sdg(0)` |
| $T$ (giro de $45°$) | $T^{\dagger}$ (giro de $-45°$) | `qc.tdg(0)` |

Desfazer funciona para **qualquer** entrada, inclusive as que você não conhece, porque a identidade vale para todos os estados ao mesmo tempo.

## Rz e a porta de fase

A porta de fase $P(\theta) = \mathrm{diag}(1, e^{i\theta})$ e a rotação $R_z(\theta) = \mathrm{diag}(e^{-i\theta/2}, e^{i\theta/2})$ diferem só por uma fase global ($R_z(\theta) = e^{-i\theta/2} P(\theta)$). Para um qubit isolado são a mesma porta. A diferença só aparece quando uma delas é controlada, como veremos na lição 1.7.

## No laboratório

Observe a coluna **fase** na tabela à direita, o ponteiro ao lado de cada amplitude e a cor do vetor. As barras de probabilidade não se mexem enquanto você gira em torno de $Z$.
