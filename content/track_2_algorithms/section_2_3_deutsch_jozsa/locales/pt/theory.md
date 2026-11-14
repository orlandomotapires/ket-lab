## O problema

Você recebe uma função $f:\{0,1\}^n \to \{0,1\}$ como caixa-preta, com uma promessa: ela é **constante** (a mesma saída para todas as entradas) ou **balanceada** (saída $0$ para metade das entradas e $1$ para a outra metade). Qual das duas?

Um algoritmo clássico precisa, no pior caso, de $2^{n-1} + 1$ consultas: se as primeiras $2^{n-1}$ derem o mesmo valor, a função ainda pode ser balanceada. O algoritmo de Deutsch-Jozsa responde com **uma única consulta**, e sem erro.

A separação é contra algoritmos clássicos *exatos*. Um algoritmo clássico **aleatorizado** consulta a função em poucas entradas sorteadas: se todas derem o mesmo valor, responde "constante". Ele erra só se a função for balanceada e as $k$ consultas coincidirem, com probabilidade de cerca de $2^{1-k}$; com algumas consultas o erro já é desprezível. A vantagem quântica aqui é real, mas é uma vantagem sobre o caso determinístico.

## O oráculo

A função entra no circuito como uma porta, o **oráculo**:

$$
U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle
$$

Aqui $x$ é o registrador de entrada (qubits 0 a 2) e $y$ é um qubit auxiliar (qubit 3). No laboratório, o oráculo é a função `oracle(qc)`, e o conteúdo dele é secreto.

## O algoritmo

1. Auxiliar em $|-\rangle$ e entrada em superposição uniforme, com Hadamards.
2. Uma consulta ao oráculo. Pelo phase kickback, cada parcela ganha o sinal $(-1)^{f(x)}$:

$$
\frac{1}{\sqrt{2^n}}\sum_x |x\rangle \;\longrightarrow\; \frac{1}{\sqrt{2^n}}\sum_x (-1)^{f(x)}|x\rangle
$$

3. Hadamards de novo na entrada. A amplitude final de $|00\dots0\rangle$ é a média dos sinais:

$$
\frac{1}{2^n}\sum_x (-1)^{f(x)}
$$

Se $f$ é constante, essa média vale $\pm 1$ e a entrada termina em $|000\rangle$ com certeza. Se é balanceada, os sinais se cancelam e $|000\rangle$ tem probabilidade zero. Uma medição decide.

## No laboratório

A aba **Amplitudes** mostra o estado do registrador de entrada, com sinal. Antes da última camada de Hadamards, veja os sinais que o oráculo imprimiu; depois dela, veja a interferência concentrar toda a amplitude em $|000\rangle$ ou zerá-la. O oráculo deste laboratório é balanceado. Na validação, o seu circuito é testado contra vários oráculos secretos, constantes e balanceados.

## Nota sobre a notação

Muitos livros escrevem o qubit 0 à **esquerda** do rótulo, como em $|x_0 x_1 x_2\rangle$. O Qiskit, e portanto este laboratório, escreve o qubit 0 à **direita**: $|q_2 q_1 q_0\rangle$. Ao comparar com um livro, os rótulos podem aparecer invertidos.
