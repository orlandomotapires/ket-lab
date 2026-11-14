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

## Flutuação estatística

Com probabilidade $p$ para um resultado e $N$ repetições, a contagem esperada é $N p$, mas a contagem real oscila em torno dela com desvio-padrão $\sigma = \sqrt{N p (1-p)}$. Para $N = 100$ e $p = \tfrac{1}{2}$, $\sigma = 5$: ver $56$ zeros em vez de $50$ é normal. Já a fração relativa oscila como $1/\sqrt{N}$, então com mais medições a proporção chega mais perto de $50\%$. Com três qubits, cada um dos $8$ resultados tem probabilidade $\tfrac{1}{8}$, e as contagens também variam de uma execução para outra.

## Outra entrada, outra fase

A Hadamard aplicada a $|1\rangle$ dá $|-\rangle$, com as mesmas probabilidades $50/50$ de $|+\rangle$. A diferença está só no sinal da amplitude de $|1\rangle$, que a medição direta não vê. A lição 1.3 trata dessa fase.

## No laboratório

- `QuantumCircuit(3, 3)` cria 3 qubits e 3 bits clássicos, onde os resultados das medições são guardados.
- Com o cursor na linha da medição, a esfera mostra **um** resultado sorteado. Use "Sortear de novo" para ver outro.
- "Simular 1024 medições" repete o circuito inteiro 1024 vezes e mostra a contagem de cada resultado.
