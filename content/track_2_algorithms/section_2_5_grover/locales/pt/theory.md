## Busca sem estrutura

Entre $N$ itens, um único está marcado e só um oráculo sabe qual. Um algoritmo clássico precisa testar, em média, $N/2$ itens. O algoritmo de Grover encontra o marcado com cerca de $\frac{\pi}{4}\sqrt{N}$ consultas: uma aceleração quadrática.

## O oráculo de fase

Aqui o oráculo inverte o sinal só do estado marcado $|\omega\rangle$:

$$
U_\omega|x\rangle = \begin{cases} -|x\rangle & \text{se } x = \omega \\ \phantom{-}|x\rangle & \text{se } x \neq \omega \end{cases}
$$

Sozinha, essa inversão não muda nenhuma probabilidade.

## O difusor: inversão em torno da média

O **difusor** $D = 2|s\rangle\langle s| - I$, onde $|s\rangle$ é a superposição uniforme, reflete cada amplitude em torno da média de todas:

$$
a_x \;\longrightarrow\; 2\bar{a} - a_x
$$

Depois do oráculo, a amplitude marcada é negativa e puxa a média um pouco para baixo. A reflexão a lança bem acima da média, e as demais encolhem um pouco.

No circuito, $D = H^{\otimes n}\,(2|0\rangle\langle 0| - I)\,H^{\otimes n}$. A reflexão em torno de $|0000\rangle$ é feita, a menos de uma fase global, com $X$ em todos os qubits, uma $Z$ multicontrolada e $X$ de novo. A $Z$ multicontrolada sai de uma Toffoli generalizada entre duas Hadamards:

```python
qc.h(3)
qc.mcx([0, 1, 2], 3)
qc.h(3)
```

## Quantas iterações

Cada iteração (oráculo e difusor) gira o estado de um ângulo $2\theta$ em direção a $|\omega\rangle$, com $\sin\theta = 1/\sqrt{N}$. Com $N = 16$, o ideal é $\left\lfloor \frac{\pi}{4}\sqrt{16} \right\rfloor = 3$ iterações, e a probabilidade do marcado chega a $96{,}1\%$. Iterar além disso passa do ponto, e a probabilidade cai.

## No laboratório

A aba **Amplitudes** mostra as 16 amplitudes com sinal e a linha tracejada da média. Avance passo a passo: o oráculo joga a barra marcada para baixo e o difusor a lança acima da média. O item marcado aqui é secreto; na validação, o circuito é testado com vários itens marcados.
