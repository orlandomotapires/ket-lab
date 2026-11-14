## Autoestados

Um estado é **autoestado** de uma porta quando ela não o altera, a não ser por um fator:

$$
U|\psi\rangle = e^{i\varphi}|\psi\rangle
$$

O fator $e^{i\varphi}$ é o **autovalor**. O estado $|-\rangle$ é autoestado da porta $X$, com autovalor $-1$:

$$
X|-\rangle = \frac{|1\rangle - |0\rangle}{\sqrt{2}} = -|-\rangle
$$

Sozinho, esse sinal é uma fase global e não muda nada que se possa medir.

## A CNOT vista de outro ângulo

Escrevendo o controle à esquerda, por clareza: com o alvo em $|-\rangle$, a CNOT aplica $X$ ao alvo só quando o controle vale $1$, e cada aplicação produz o sinal $-1$:

$$
\text{CNOT}\,|x\rangle|-\rangle = (-1)^x\,|x\rangle|-\rangle
$$

O alvo continua em $|-\rangle$. O sinal ficou na parcela do controle. Se o controle está em superposição, o sinal deixa de ser global e vira fase relativa:

$$
\text{CNOT}\,|+\rangle|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}\,|-\rangle = |-\rangle|-\rangle
$$

## Phase kickback

A porta age "no alvo", mas quem muda é o controle. Esse efeito se chama **phase kickback** e vale para qualquer porta controlada: se o alvo é autoestado de $U$ com autovalor $e^{i\varphi}$, a fase $e^{i\varphi}$ volta para a parcela $|1\rangle$ do controle.

## Por que isso importa

É o mecanismo de quase todos os algoritmos desta trilha. Deutsch-Jozsa e Bernstein-Vazirani usam um qubit auxiliar em $|-\rangle$ para transformar a resposta de uma função em fase. A estimação de fase usa o mesmo truque com uma porta qualquer, e o algoritmo de Shor é construído sobre ela.

## No laboratório

Nas esferas de Bloch, o vetor do controle salta de $+x$ para $-x$ no passo da CNOT, enquanto o do alvo fica parado. Compare com o que acontece se o alvo estiver em $|0\rangle$ ou $|1\rangle$: aí a CNOT emaranha os qubits, como na lição de estados de Bell.
