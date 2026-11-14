## Além dos polos

Na lição anterior o qubit só visitou $|0\rangle$ e $|1\rangle$. A porta **Hadamard** ($H$) leva o vetor ao equador da esfera:

$$
H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle
$$

$$
H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}} = |-\rangle
$$

Em $|+\rangle$ as duas amplitudes valem $\frac{1}{\sqrt{2}}$, então cada resultado tem probabilidade $\left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2}$. Isso é uma **superposição uniforme**.

## O que a medição faz

Medir não revela um valor que já estava lá. A medição **sorteia** um resultado, com as probabilidades dadas pelas amplitudes, e o estado passa a ser o resultado sorteado: o vetor salta do equador para um dos polos. Esse salto é o **colapso**.

Por isso um qubit em $|+\rangle$ seguido de uma medição é um gerador de bits aleatórios. A aleatoriedade não vem de desconhecermos algum detalhe do sistema: ela faz parte da teoria.

## No laboratório

- `QuantumCircuit(1, 1)` cria 1 qubit e 1 bit clássico, onde o resultado da medição é guardado.
- Com o cursor na linha da medição, a esfera mostra **um** resultado sorteado. Use "Sortear de novo" para ver outro.
- "Simular 1024 medições" repete o circuito inteiro 1024 vezes e mostra a contagem de cada resultado.
