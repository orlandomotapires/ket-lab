## Amplitudes podem se cancelar

Probabilidades só se somam. Amplitudes têm sinal (e fase), então também podem **se cancelar**. Isso é a interferência, e é dela que os algoritmos quânticos tiram sua vantagem.

Veja duas Hadamard seguidas. A primeira leva $|0\rangle$ a $|+\rangle$. A segunda age em cada parcela:

$$
H|+\rangle = \frac{H|0\rangle + H|1\rangle}{\sqrt{2}}
= \frac{(|0\rangle + |1\rangle) + (|0\rangle - |1\rangle)}{2}
= |0\rangle
$$

As duas contribuições para $|1\rangle$ têm sinais opostos e somem: **interferência destrutiva**. As duas para $|0\rangle$ se reforçam: **interferência construtiva**. O resultado é $HH = I$.

## A fase escolhe o que é cancelado

Se a fase relativa for invertida no meio do caminho, o cancelamento troca de lado. É assim que uma porta que "não muda probabilidades" passa a decidir o resultado da medição.

Essa é a razão de a fase da lição anterior importar: sozinha ela é invisível para a medição, mas uma Hadamard depois dela a transforma em probabilidade.

## Medir em outra base

A medição padrão distingue $|0\rangle$ de $|1\rangle$ (a **base Z**) e não distingue $|+\rangle$ de $|-\rangle$. Para distingui-los, aplica-se uma Hadamard antes de medir: ela leva $|+\rangle$ a $|0\rangle$ e $|-\rangle$ a $|1\rangle$. Isso equivale a medir na **base X**.

## Medir no meio do caminho

Em $HH = I$, o cancelamento das duas parcelas de $|1\rangle$ só acontece porque as duas amplitudes chegam **juntas** à segunda Hadamard. Se você medir o qubit entre as duas Hadamard, a medição já sorteou $0$ ou $1$ e o estado colapsou para um polo. A segunda Hadamard recebe então $|0\rangle$ ou $|1\rangle$ e devolve $|+\rangle$ ou $|-\rangle$, com $50\%$ de chance para cada resultado: a interferência desapareceu. Observar o caminho destrói a interferência.

## A ordem das portas importa

Em geral $AB \neq BA$. Aplicar $H$ e depois $S$ a $|0\rangle$ dá $|{+i}\rangle$, mas aplicar $S$ e depois $H$ dá $|+\rangle$. Por isso o código do circuito se lê de cima para baixo, na ordem em que as portas agem, e o produto de matrizes se escreve ao contrário.

## No laboratório

Percorra o circuito com a linha do tempo e acompanhe a tabela de amplitudes: observe o sinal de cada amplitude antes da última Hadamard e o que sobra depois dela.
