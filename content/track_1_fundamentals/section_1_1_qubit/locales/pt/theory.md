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

## Como usar o laboratório

- A visualização acompanha a **linha onde está o cursor**: ela mostra o estado do qubit depois de tudo que foi executado até ali.
- Você não precisa clicar em "executar". O estado é recalculado quando você para de digitar.
- Experimente à vontade: aplicar `qc.x(0)` duas vezes, por exemplo, e ver o que acontece.
