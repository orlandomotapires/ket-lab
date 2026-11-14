## Circuitos com parâmetros

Até aqui, cada porta tinha um ângulo fixo. Um **circuito variacional** tem ângulos ajustáveis $\vec\theta$, e o resultado de uma medição vira uma função deles:

$$
f(\vec\theta) = \langle \psi(\vec\theta) |\, O \,| \psi(\vec\theta) \rangle
$$

onde $O$ é um observável, como $Z$. Um computador clássico escolhe os ângulos, o quântico avalia $f$, e o clássico ajusta os ângulos para minimizar $f$. Esse ciclo híbrido é a base do VQE, do QAOA e das redes neurais quânticas das próximas lições.

O circuito com parâmetros se chama **ansatz**. Um bom ansatz alcança estados suficientes para conter a resposta (**expressibilidade**) sem ser tão grande que fique impossível de treinar.

## PennyLane

Nesta trilha os circuitos são escritos em PennyLane, que calcula gradientes de circuitos quânticos:

- `qml.device("default.qubit", wires=1)` cria um simulador de 1 qubit;
- `@qml.qnode(dev)` transforma uma função Python num circuito executável, o **QNode**;
- a função aplica portas, como `qml.RX(θ, wires=0)`, e devolve uma medição, como `qml.expval(qml.PauliZ(0))`;
- `from pennylane import numpy as np` fornece um NumPy que o PennyLane sabe derivar.

A plataforma mostra os qubits na mesma ordem das outras trilhas: o qubit 0 fica à direita nos rótulos.

## A regra de parameter-shift

Para minimizar $f$, é preciso o gradiente. Num computador quântico real não dá para "olhar dentro" do circuito, e diferenças finitas, $[f(\theta + \epsilon) - f(\theta)]/\epsilon$, se perdem no ruído das medições. Para portas de rotação como $R_X$ e $R_Y$, porém, a derivada é exata a partir de duas execuções do próprio circuito:

$$
\frac{\partial f}{\partial \theta_i} = \frac{f\!\left(\theta_i + \frac{\pi}{2}\right) - f\!\left(\theta_i - \frac{\pi}{2}\right)}{2}
$$

com os demais parâmetros fixos. Os deslocamentos são grandes, $\pm\pi/2$, então o ruído de medição pesa pouco. Essa é a **regra de parameter-shift**.

## Gradiente descendente

Com o gradiente, cada passo anda um pouco no sentido de descida:

$$
\vec\theta \;\leftarrow\; \vec\theta - \eta\, \nabla f(\vec\theta)
$$

A **taxa de aprendizado** $\eta$ controla o tamanho do passo: pequena demais torna o treino lento; grande demais faz o otimizador pular o mínimo.

## Neste laboratório

O custo é $\langle Z\rangle$ depois de $R_X(\theta_0)$ e $R_Y(\theta_1)$, que vale $\cos\theta_0 \cos\theta_1$. O mínimo, $-1$, é o polo sul da esfera de Bloch.

- A aba **Paisagem** mostra o custo para todos os ângulos, com a trajetória do seu otimizador.
- A aba **Convergência** mostra o custo passo a passo.
- As **Esferas de Bloch** mostram o estado com os parâmetros finais.

Como o treino leva alguns instantes, o código roda quando você clica em **Executar** ou aperta Ctrl+Enter.
