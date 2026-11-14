## Quando não sabemos o estado

Até aqui, o qubit estava sempre num estado bem definido $|\psi\rangle$: um **estado puro**. Num computador real, o ruído age ao acaso: às vezes uma porta erra, às vezes não. Depois disso, só sabemos que o qubit está em $|\psi_1\rangle$ com probabilidade $p_1$, em $|\psi_2\rangle$ com probabilidade $p_2$ e assim por diante. Isso é um **estado misto**.

Um estado misto não é uma superposição. A superposição $\frac{|0\rangle + |1\rangle}{\sqrt2}$ é um estado puro, com fase bem definida; uma moeda que dá $|0\rangle$ ou $|1\rangle$ com 50% cada não tem fase nenhuma.

## A matriz densidade

Os dois casos cabem numa mesma descrição, a **matriz densidade**:

$$
\rho = \sum_i p_i\, |\psi_i\rangle\langle\psi_i|
$$

- A diagonal dá as probabilidades de medição: $P(0) = \rho_{00}$ e $P(1) = \rho_{11}$.
- A **pureza** $\mathrm{Tr}(\rho^2)$ vale $1$ para um estado puro e é menor que $1$ para um misto; para 1 qubit, o mínimo é $1/2$.
- Na esfera de Bloch, estados puros ficam na superfície e mistos ficam no interior, com o vetor encurtado.

Os qubits emaranhados da Trilha 1 encolhiam na esfera pelo mesmo motivo: o estado de um qubit de um par de Bell, olhado sozinho, é misto. Ele é obtido pelo **traço parcial**, que descarta o outro qubit.

## Canais de ruído

Uma operação ruidosa age em $\rho$ por meio de **operadores de Kraus** $K_k$:

$$
\rho \;\longrightarrow\; \sum_k K_k\, \rho\, K_k^\dagger, \qquad \sum_k K_k^\dagger K_k = I
$$

Um erro que aplica $X$ com probabilidade $p_x$, $Z$ com $p_z$ e nada no resto tem $K_0 = \sqrt{1-p_x-p_z}\,I$, $K_1 = \sqrt{p_x}\,X$ e $K_2 = \sqrt{p_z}\,Z$. Os canais mais comuns têm nome: *bit flip*, *phase flip*, despolarizante, amortecimento de amplitude.

## Erro não é o mesmo que resposta errada

A probabilidade de **um erro acontecer** não é a probabilidade de **a resposta sair errada**. O efeito de um erro depende de onde ele ocorre e do que vem depois: um $Z$ seguido de Hadamard vira um $X$ completo, enquanto um $X$ entre $T$ e $T^\dagger$ vira uma rotação que só às vezes muda o resultado. Por isso a correção de erros, na próxima lição, olha para o tipo de erro e não só para a frequência.

## No laboratório

O dispositivo `default.mixed` simula a matriz densidade. Nas **esferas de Bloch**, acompanhe o vetor encolher no passo do erro; o painel mostra a pureza do estado. A aba **Registrador** mostra $P(0)$ e $P(1)$.
