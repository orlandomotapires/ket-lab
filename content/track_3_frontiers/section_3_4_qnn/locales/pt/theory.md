## Aprendizado de máquina com circuitos

Um classificador recebe um ponto $\vec x$ e devolve uma classe. Num **classificador quântico**, o ponto entra no circuito como ângulos de rotação, e a classe sai de uma medição. Os pesos treináveis são outros ângulos, ajustados por gradiente como nas lições anteriores.

## Codificar os dados

Antes de processar um dado clássico, é preciso colocá-lo num estado quântico. As formas mais comuns:

- **Codificação por ângulo**: cada coordenada vira o ângulo de uma rotação, como $R_X(x_0)$ e $R_Y(x_1)$. É simples de preparar, mas usa um qubit (ou uma porta) por coordenada.
- **Codificação por amplitude**: os $2^n$ números do dado viram as amplitudes de $n$ qubits. É compacta, mas difícil de preparar.
- **Codificação por fase**: os dados entram como fases relativas.

Aqui usamos codificação por ângulo.

## Data re-uploading

Se os dados entram uma única vez, a saída do circuito é uma função trigonométrica simples de $\vec x$ e não consegue desenhar fronteiras complicadas. A saída é **recarregar** os dados várias vezes, intercalando com camadas treináveis:

$$
U(\vec x, \vec w) = W_L\, S(\vec x)\, W_{L-1}\, S(\vec x) \cdots W_1\, S(\vec x)\, W_0
$$

Cada recarga enriquece a função que o circuito representa, como os termos a mais de uma série de Fourier.

## O classificador

- **Entrada:** pontos $(x_0, x_1)$ em dois círculos concêntricos; os de fora têm classe $+1$ e os de dentro, $-1$. Uma reta não separa as duas classes.
- **Saída:** $\langle Z_0 \rangle$, entre $-1$ e $+1$; o sinal é a classe prevista.
- **Treino:** minimizar o erro quadrático médio entre $\langle Z_0\rangle$ e os rótulos, com o otimizador Adam.

O circuito processa todos os pontos de uma vez: quando `x` tem forma $(N, 2)$, o PennyLane executa as $N$ versões do circuito em paralelo (*broadcasting*).

## Generalizar, não decorar

O que importa é acertar pontos que o modelo **não viu**. Por isso a validação usa um conjunto de teste separado. Acurácia alta no treino e baixa no teste é sinal de que o modelo decorou os exemplos (*overfitting*).

## No laboratório

- A aba **Fronteira** mostra a saída do circuito em todo o plano, com os pontos de treino por cima.
- A aba **Convergência** mostra a perda a cada época.

O código inicial carrega os dados uma única vez. Clique em **Executar** (ou Ctrl+Enter) para treinar.
