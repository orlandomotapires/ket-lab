## Por que corrigir erros

Qubits reais erram: o ruído da lição anterior se acumula a cada porta. Para computações longas, é preciso detectar e desfazer erros durante o cálculo. Isso parece impossível por três motivos: não dá para copiar um estado desconhecido (teorema da não clonagem), medir o qubit destrói a superposição, e os erros são contínuos. A correção de erros quânticos contorna os três.

## Redundância sem cópia

Classicamente, basta repetir: $0 \to 000$, e a maioria vence. Quanticamente, não se copia $|\psi\rangle$, mas pode-se emaranhar a base:

$$
\alpha|0\rangle + \beta|1\rangle \;\longrightarrow\; \alpha|000\rangle + \beta|111\rangle
$$

com duas CNOTs. Isso não são três cópias de $|\psi\rangle$: é um único estado lógico espalhado por três qubits.

## Medir o erro, não o estado

Um bit flip no qubit 1 leva a $\alpha|010\rangle + \beta|101\rangle$. Medir os qubits destruiria $\alpha$ e $\beta$; mas as **paridades** (se dois qubits são iguais ou diferentes) não dependem deles. Duas ancillas guardam as paridades dos qubits 0–1 e 1–2. O par de resultados, a **síndrome**, aponta o erro:

| Síndrome (a₃ a₄) | Erro | Correção |
| :-- | :-- | :-- |
| 00 | nenhum | nenhuma |
| 10 | X no qubit 0 | X no 0 |
| 11 | X no qubit 1 | X no 1 |
| 01 | X no qubit 2 | X no 2 |

A correção pode ser feita sem medir, com portas Toffoli controladas pelas ancillas (é o princípio da medição adiada).

## Os limites deste código

- **Dois flips** dão a síndrome de um flip só no qubit restante: o código "corrige" o qubit errado e produz um erro lógico.
- **Phase flips** ($Z$) não mudam nenhuma paridade: passam despercebidos. Um código análogo na base $X$ corrige $Z$, e o código de Shor, de 9 qubits, junta os dois e corrige qualquer erro de um qubit.

## O limiar

Se cada qubit sofre um bit flip com probabilidade $p$, o código falha só quando dois ou três qubits erram:

$$
P_{\text{sucesso}} = 1 - 3p^2 + 2p^3
$$

Para $p < \tfrac{1}{2}$ isso é melhor que $1 - p$, o qubit sozinho. A ideia de um **limiar** abaixo do qual codificar ajuda é o que torna possível a computação quântica tolerante a falhas.

## No laboratório

- Os botões escolhem o erro injetado. Experimente os que o código não corrige.
- Na aba **Registrador**, com o cursor depois da síndrome, aparecem os bits das ancillas.
- Nas **Esferas de Bloch**, acompanhe os qubits de dados.
- A aba **Limiar** compara o qubit protegido com o desprotegido.
