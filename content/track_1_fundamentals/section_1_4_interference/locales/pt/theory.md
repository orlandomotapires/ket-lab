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

## No laboratório

Percorra o circuito com a linha do tempo e acompanhe a tabela de amplitudes: observe o sinal de cada amplitude antes da última Hadamard e o que sobra depois dela.
