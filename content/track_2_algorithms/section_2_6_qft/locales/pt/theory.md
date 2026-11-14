## Da posição para a frequência

A transformada de Fourier discreta leva uma sequência de números ao espectro de frequências dela. A **transformada quântica de Fourier** (QFT) faz o mesmo com as amplitudes de um estado de $n$ qubits, com $N = 2^n$:

$$
\text{QFT}\,|x\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi i\, xk/N}\,|k\rangle
$$

Todas as saídas têm a mesma probabilidade, $1/N$. A informação sobre $x$ fica inteiramente nas **fases**: a amplitude de $|k\rangle$ gira $xk/N$ de volta completa.

## A forma produto

A mesma expressão se fatora qubit a qubit: cada qubit termina no equador da esfera de Bloch, com uma fase proporcional a $x$. Um deles gira $x/2$ de volta, outro $x/4$, outro $x/8$. É essa forma que dá o circuito: uma Hadamard cria o equador, e fases controladas pelos outros qubits acrescentam as frações menores.

## O circuito

Para 3 qubits, começando pelo mais significativo (qubit 2):

1. $H$ no qubit 2; depois a fase $\pi/2$ controlada pelo qubit 1 e a fase $\pi/4$ controlada pelo qubit 0.
2. $H$ no qubit 1; depois a fase $\pi/2$ controlada pelo qubit 0.
3. $H$ no qubit 0.
4. `swap` entre os qubits 0 e 2: o circuito produz os qubits na ordem inversa.

A fase controlada é `qc.cp(ângulo, controle, alvo)`, a porta

$$
R(\varphi) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\varphi} \end{pmatrix}
$$

aplicada ao alvo quando o controle vale $1$.

## Duas observações

**Os `swap` finais.** Sem o passo 4, o circuito calcula a QFT com os qubits de saída em ordem inversa. Alguns textos omitem os `swap` e leem o resultado de trás para frente, ou deixam a troca por conta de quem usa. Aqui eles ficam no circuito, para que a saída bata com a DFT na convenção do Qiskit.

**Hadamard e Fourier.** A transformada de Hadamard $H^{\otimes n}$ é a transformada de Fourier sobre o grupo $(\mathbb{Z}_2)^n$, em que os "caracteres" são $(-1)^{s\cdot x}$. Com um único qubit, $2^1 = 2$ e a QFT coincide com a Hadamard. É o que fez o Bernstein-Vazirani funcionar; a QFT usada aqui é a versão sobre $\mathbb{Z}_{2^n}$, com fases $e^{2\pi i\,xk/2^n}$.

## No laboratório

A função `prepare_input(qc)` prepara a entrada $|x\rangle$, aqui $|101\rangle = |5\rangle$. A aba **Fases** mostra um mostrador por estado: o tamanho indica a probabilidade e o ponteiro, a fase. Depois da QFT, os ponteiros giram $5k/8$ de volta, avançando em passos iguais de um estado para o seguinte. Na validação, o circuito é testado com várias entradas, inclusive superposições.
