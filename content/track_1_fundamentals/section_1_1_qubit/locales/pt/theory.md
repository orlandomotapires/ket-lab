## Do bit ao qubit

Um bit clássico só pode estar em um de dois valores: $0$ ou $1$. Um **qubit** também tem dois estados de referência, escritos $|0\rangle$ e $|1\rangle$, mas pode estar em qualquer combinação deles:

$$
|\psi\rangle = \alpha|0\rangle + \beta|1\rangle
$$

Os números $\alpha$ e $\beta$ são as **amplitudes**. Elas não são probabilidades, mas determinam as probabilidades: ao medir o qubit, você obtém $0$ com probabilidade $|\alpha|^2$ e $1$ com probabilidade $|\beta|^2$. Como algum resultado sempre acontece,

$$
|\alpha|^2 + |\beta|^2 = 1
$$

## A Esfera de Bloch

Todo estado de um qubit corresponde a um ponto na superfície de uma esfera. O polo norte é $|0\rangle$ e o polo sul é $|1\rangle$. À direita, o vetor mostra onde o seu qubit está agora.

Nesta lição o vetor só visita os dois polos. Os outros pontos da esfera aparecem a partir da próxima.

## A porta X

Portas quânticas movem o vetor pela esfera. A **Pauli-X** o gira $180°$ em torno do eixo $X$:

$$
X|0\rangle = |1\rangle \qquad X|1\rangle = |0\rangle
$$

Ela faz com o qubit o que o `NOT` faz com um bit.

## Normalização

Nem todo par de números é um estado. As amplitudes precisam satisfazer $|\alpha|^2 + |\beta|^2 = 1$. Por exemplo, $(0{,}6;\ 0{,}8)$ é um estado válido, pois $0{,}36 + 0{,}64 = 1$. Já $(0{,}6;\ 0{,}6)$ não é: a soma dá $0{,}72$. Para torná-lo válido, divide-se o vetor pela sua norma (aqui, $\sqrt{0{,}72}$). As portas quânticas preservam essa soma, por isso um circuito nunca produz um vetor fora da esfera.

## Fase global

Multiplicar o estado inteiro por $e^{i\gamma}$ não muda nenhuma probabilidade, nem o resultado de qualquer medição possível: $|\psi\rangle$ e $e^{i\gamma}|\psi\rangle$ são fisicamente o mesmo estado, e a esfera de Bloch os desenha no mesmo ponto. O que importa é a fase **relativa** entre $\alpha$ e $\beta$, assunto da lição 1.3.

Por isso $Y$ e $R_x(\pi)$ levam $|0\rangle$ ao mesmo estado físico que $X$ leva: os resultados diferem só por uma fase global ($Y|0\rangle = i|1\rangle$ e $R_x(\pi)|0\rangle = -i|1\rangle$).

## Como usar o laboratório

- A visualização acompanha a **linha onde está o cursor**: ela mostra o estado do qubit depois de tudo que foi executado até ali.
- Você não precisa clicar em "executar". O estado é recalculado quando você para de digitar.
- Experimente à vontade: aplicar `qc.x(0)` duas vezes, por exemplo, e ver o que acontece.
