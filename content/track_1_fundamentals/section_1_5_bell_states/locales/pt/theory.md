## Dois qubits

Com dois qubits existem quatro estados de base: $|00\rangle$, $|01\rangle$, $|10\rangle$ e $|11\rangle$. Um estado geral é uma combinação dos quatro:

$$
|\psi\rangle = a_{00}|00\rangle + a_{01}|01\rangle + a_{10}|10\rangle + a_{11}|11\rangle
$$

Com $n$ qubits são $2^n$ amplitudes. É esse crescimento que faz computadores clássicos terem dificuldade em simular computadores quânticos.

## A ordem dos qubits

Nesta plataforma, como no Qiskit, o **qubit 0 fica à direita** no rótulo: em $|q_1 q_0\rangle$, o estado $|01\rangle$ significa qubit 0 em $1$ e qubit 1 em $0$. A convenção parece invertida no começo, mas é a mesma de um número binário: o bit menos significativo fica à direita.

> **Atenção:** muitos livros e cursos escrevem o qubit 0 à **esquerda**. Ao comparar com outra fonte, os rótulos aparecem invertidos: o que aqui é $|01\rangle$ lá é $|10\rangle$. Ao ler um resultado, confira sempre qual convenção está em uso.

## Estados que se separam e estados que não

Se cada qubit tem o seu próprio estado, o estado conjunto é o **produto tensorial** dos dois:

$$
|q_1\rangle \otimes |q_0\rangle = |+\rangle \otimes |0\rangle = \frac{|00\rangle + |10\rangle}{\sqrt{2}}
$$

Aqui o qubit 1 está em $|+\rangle$ e o qubit 0 está em $|0\rangle$. O fator da esquerda é sempre o de maior índice, de acordo com a convenção acima.

Alguns estados de dois qubits **não** podem ser escritos assim. O mais famoso é o estado de Bell

$$
|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

Não existe estado do qubit 0 e estado do qubit 1 cujo produto dê $|\Phi^+\rangle$. Os dois qubits estão **emaranhados**: o estado existe só para o par.

## A porta CNOT

A CNOT (*controlled NOT*) age em dois qubits: inverte o **alvo** quando o **controle** vale $1$ e não faz nada quando vale $0$. Aplicada sobre uma superposição no controle, ela cria emaranhamento:

$$
\text{CNOT}\,\frac{|00\rangle + |01\rangle}{\sqrt{2}} = \frac{|00\rangle + |11\rangle}{\sqrt{2}}
$$

## Um teste para o produto

Para um estado puro de dois qubits, há um teste simples. Ele é separável (um produto) se e somente se

$$
a_{00}\,a_{11} = a_{01}\,a_{10}
$$

Se $|\psi\rangle = (\alpha_1|0\rangle + \beta_1|1\rangle)\otimes(\alpha_0|0\rangle + \beta_0|1\rangle)$, então $a_{00}a_{11} = \alpha_1\alpha_0\beta_1\beta_0 = a_{01}a_{10}$. Para $|\Phi^+\rangle$, $a_{00}a_{11} = \tfrac{1}{2}$ mas $a_{01}a_{10} = 0$: não é um produto, logo está emaranhado. Já $(|00\rangle + |01\rangle - |10\rangle - |11\rangle)/2$ tem as quatro amplitudes não nulas e passa no teste, pois é $|-\rangle\otimes|+\rangle$. Contar amplitudes não nulas não basta.

## O que observar no laboratório

- **Q-Sphere**: cada ponto é um estado da base. Os pontos ficam mais ao sul quanto mais $1$s o rótulo tem; o tamanho indica a probabilidade e a cor, a fase.
- **Esferas de Bloch**: um qubit emaranhado não tem estado próprio. O vetor dele encolhe até o centro da esfera ($|r| = 0$).
- **Emaranhamento**: a concorrência vai de $0$ (estado separável) a $1$ (emaranhamento máximo).
