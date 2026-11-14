## O problema Max-Cut

Dado um grafo, divida os vértices em dois grupos de modo que o maior número possível de arestas ligue vértices de grupos diferentes (arestas "cortadas"). É um problema NP-difícil: para grafos grandes, não se conhece algoritmo eficiente que garanta o ótimo. Aparece em projeto de circuitos, agrupamento de dados e física estatística.

Neste grafo de 5 vértices e 6 arestas, o melhor corte vale 5.

## Do grafo para os qubits

Cada vértice vira um qubit: $|0\rangle$ e $|1\rangle$ indicam o grupo. Uma aresta $(i, j)$ está cortada quando os bits diferem, isto é, quando $Z_i Z_j = -1$. Então

$$
\text{corte} = \sum_{(i,j)} \frac{1 - Z_i Z_j}{2}
$$

e maximizar o corte é o mesmo que **minimizar** a energia de Ising $H_C = \sum_{(i,j)} Z_i Z_j$. No laboratório, `cost_h` é esse $H_C$.

## O QAOA

O *Quantum Approximate Optimization Algorithm* alterna dois tipos de camada, partindo da superposição uniforme:

$$
|\vec\gamma, \vec\beta\rangle = U_M(\beta_p)\,U_C(\gamma_p) \cdots U_M(\beta_1)\,U_C(\gamma_1)\,|+\rangle^{\otimes n}
$$

- **Custo**, $U_C(\gamma) = e^{-i\gamma H_C/2}$: uma `IsingZZ(γ)` em cada aresta. Imprime nas amplitudes uma fase que depende do corte.
- **Mistura**, $U_M(\beta) = e^{-i\beta \sum X}$: um `RX(2β)` em cada qubit. Transforma essas fases em mudanças de probabilidade, por interferência.

Um otimizador clássico ajusta os $2p$ ângulos para minimizar $\langle H_C \rangle$. É o mesmo ciclo híbrido das lições anteriores.

## A razão de aproximação

O resultado é medido pela **razão de aproximação**: o corte esperado do estado final dividido pelo corte máximo. Uma razão de 1 significaria medir sempre a solução ótima. Quanto maior $p$, mais perto de 1 o QAOA pode chegar; com $p \to \infty$, ele recupera o recozimento quântico (*quantum annealing*).

## No laboratório

- A aba **Grafo** mostra os vértices coloridos pelo corte mais provável, com as arestas cortadas destacadas, e a razão de aproximação.
- A aba **Convergência** mostra a razão a cada passo, com o limiar de 0,85.
- A aba **Registrador** mostra a probabilidade de cada uma das 32 divisões.

O código inicial usa uma camada só. Clique em **Executar** (ou Ctrl+Enter) para treinar.
