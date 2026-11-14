## Fatorar é encontrar um período

A segurança da criptografia RSA depende de ser difícil fatorar números grandes. Shor mostrou que fatorar um número composto $N$ se reduz a encontrar o **período** da função

$$
f(x) = a^x \bmod N
$$

para um $a$ escolhido ao acaso, sem divisores em comum com $N$. O período $r$ é o menor inteiro positivo com $a^r \bmod N = 1$.

Com $N = 15$ e $a = 7$, a sequência $7^x \bmod 15$ é $1, 7, 4, 13, 1, 7, 4, 13, \dots$ e o período é $r = 4$.

## Do período aos fatores

Se $r$ é par, $a^r - 1 = (a^{r/2} - 1)(a^{r/2} + 1)$ é múltiplo de $N$, e cada um dos dois fatores compartilha um divisor com $N$:

$$
\text{mdc}(a^{r/2} - 1,\, N) \qquad \text{e} \qquad \text{mdc}(a^{r/2} + 1,\, N)
$$

Com $r = 4$: $7^2 = 49$, $\text{mdc}(48, 15) = 3$ e $\text{mdc}(50, 15) = 5$.

## A parte quântica

A multiplicação modular $U|y\rangle = |7y \bmod 15\rangle$ é uma operação unitária, com autovalores $e^{2\pi i\,s/r}$. Começando o registrador de trabalho em $|1\rangle$ e aplicando a estimação de fase da lição anterior, a contagem mede $s/r$ para um $s$ sorteado entre $0$ e $r - 1$. Com 4 qubits de contagem, os resultados possíveis são $16 \cdot s/4 = 0,\ 4,\ 8,\ 12$.

## Pós-processamento clássico

Para cada resultado $m$, a fase é $m/16$. A fração de denominador pequeno mais próxima revela $r$:

```python
from fractions import Fraction
Fraction(12 / 16).limit_denominator(15)   # 3/4, então r = 4
```

Nem todo resultado serve: $m = 0$ não informa nada, e $m = 8$ dá $r = 2$, que não é o período (confira: $7^2 \bmod 15 = 4 \neq 1$). Por isso a verificação `pow(a, r, N) == 1` vem antes de usar $r$, e o algoritmo combina várias medições.

## Como escolher $a$ e quando falha

Escolha $a$ ao acaso com $1 < a < N$. Se $\text{mdc}(a, N) \neq 1$, o próprio mdc já é um fator e não é preciso quântica. Caso contrário, uma tentativa falha quando:

- $r$ é **ímpar**: não dá para dividir $a^r - 1$ em dois fatores;
- $a^{r/2} \equiv -1 \pmod N$: então $a^{r/2} + 1$ é múltiplo de $N$ e os dois mdc valem $1$ e $N$. Exemplo: $a = 14 \equiv -1 \pmod{15}$ tem $r = 2$ e $14^1 \equiv -1$, e nada se aprende.

Para um $a$ sorteado, cada execução acerta com probabilidade acima de 50%; se falhar, sorteia-se outro $a$ e repete-se.

## O passo de frações contínuas

O resultado $m$ aproxima $s/r$ por $m/2^t$. Para recuperar $r$, usa-se a expansão em fração contínua de $m/2^t$ e pega-se o convergente de denominador no máximo $N$. É o que `limit_denominator(N)` faz. Com $2^t \geq N^2$ (para $N = 15$, $t = 8$ qubits de contagem), o convergente certo é garantido; aqui, com $N = 15$ e 4 qubits, o problema é pequeno o bastante para funcionar assim mesmo.

## No laboratório

- `apply_controlled_mod_mult(qc, controle, potência)` multiplica o registrador de trabalho (qubits 4 a 7) por $7^{\text{potência}} \bmod 15$, controlada pelo qubit indicado.
- `inverse_qft(qc, qubits)` é a QFT inversa.
- `run_shots(qc)` executa o circuito 1024 vezes e devolve as contagens.

A aba **Período** mostra $7^x \bmod 15$; a aba **Registrador** mostra os picos da contagem.
