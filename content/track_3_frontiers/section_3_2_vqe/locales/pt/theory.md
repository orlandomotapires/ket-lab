## Química num computador quântico

As propriedades de uma molécula (como ela se liga, reage, absorve luz) vêm da energia dos seus elétrons. Calcular essa energia exatamente custa, num computador clássico, um esforço que cresce exponencialmente com o tamanho da molécula. Simular sistemas quânticos é a aplicação mais natural de um computador quântico.

## Do Hamiltoniano aos qubits

A energia é dada pelo **Hamiltoniano** $H$ dos elétrons. Na base mínima STO-3G, o H₂ tem 4 orbitais de spin; cada um vira um qubit (ocupado = $|1\rangle$). O **mapeamento de Jordan-Wigner** reescreve $H$ como uma soma de produtos de matrizes de Pauli:

$$
H = \sum_j c_j\, P_j, \qquad P_j \in \{I, X, Y, Z\}^{\otimes 4}
$$

No laboratório, `H` já está pronto: são 15 termos, calculados para a distância de equilíbrio de 0,74 Å.

## O princípio variacional

Para qualquer estado $|\psi\rangle$:

$$
E(\vec\theta) = \langle \psi(\vec\theta) | H | \psi(\vec\theta) \rangle \;\ge\; E_0
$$

A energia de qualquer estado é maior ou igual à do estado fundamental $E_0$. Então basta preparar estados com um circuito parametrizado e minimizar $E(\vec\theta)$: quanto menor a energia, mais perto do estado fundamental. Esse é o **VQE** (*variational quantum eigensolver*).

## O ansatz químico

1. **Hartree-Fock**: os dois elétrons nos dois orbitais de menor energia, `hf_state = [1, 1, 0, 0]`. É uma boa aproximação, mas ignora a correlação entre os elétrons.
2. **Excitação dupla**: `qml.DoubleExcitation(θ)` mistura o estado de Hartree-Fock com o estado em que os dois elétrons sobem juntos para os orbitais vazios:

$$
\cos\tfrac{\theta}{2}\,|1100\rangle \;-\; \sin\tfrac{\theta}{2}\,|0011\rangle
$$

(na notação do PennyLane, com o fio 0 à esquerda). Para o H₂ nessa base, um único parâmetro basta para chegar à energia exata.

## Precisão química

A energia de Hartree-Fock é $-1{,}1168$ Ha e a exata é $-1{,}1373$ Ha (a energia total do estado fundamental, em hartrees). A diferença parece pequena, mas decide a química. O padrão é chegar a $1{,}6$ mHa do valor exato (cerca de 1 kcal/mol): a **precisão química**.

## No laboratório

- A aba **Convergência** mostra a energia a cada passo, com a linha da energia exata e a faixa de precisão química.
- A aba **Dissociação** mostra como a energia muda com a distância entre os átomos: a curva exata, a de Hartree-Fock e o seu resultado em 0,74 Å.
- Na **Q-Sphere** aparecem os dois estados que o ansatz mistura.

Clique em **Executar** (ou Ctrl+Enter) para treinar.
