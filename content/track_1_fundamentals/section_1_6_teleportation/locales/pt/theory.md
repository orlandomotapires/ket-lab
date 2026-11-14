## O problema

Alice tem um qubit num estado $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ que ela **não conhece**, e quer entregá-lo a Bob, que está longe. Ela não pode medir o qubit e mandar os números: uma medição dá só um bit e destrói a superposição. Ela também não pode copiá-lo: o **teorema da não clonagem** proíbe copiar um estado quântico desconhecido.

## O recurso: um par emaranhado

Antes de se separarem, Alice e Bob criaram um par de Bell: o qubit 1 ficou com Alice e o qubit 2 com Bob. Com esse par e **dois bits de comunicação clássica**, o estado pode ser transferido.

## O protocolo

1. **Par de Bell** entre os qubits 1 e 2: $H$ no qubit 1 e CNOT de 1 para 2.
2. **Alice entrelaça** o seu estado com a metade dela do par: CNOT de 0 para 1, depois $H$ no qubit 0.
3. **Alice mede** os qubits 0 e 1 e envia os dois bits a Bob.
4. **Bob corrige**: aplica $X$ se o bit do qubit 1 for $1$ e depois $Z$ se o bit do qubit 0 for $1$.

Depois do passo 3, o qubit de Bob está em um de quatro estados, conforme o resultado da medição. Cada um é $|\psi\rangle$ com um "defeito" conhecido, e a correção do passo 4 desfaz exatamente esse defeito:

| Bits medidos (q1 q0) | Estado de Bob | Correção |
| :-- | :-- | :-- |
| 00 | $\alpha|0\rangle + \beta|1\rangle$ | nenhuma |
| 01 | $\alpha|0\rangle - \beta|1\rangle$ | $Z$ |
| 10 | $\beta|0\rangle + \alpha|1\rangle$ | $X$ |
| 11 | $\beta|0\rangle - \alpha|1\rangle$ | $X$, depois $Z$ |

## Correções condicionais no Qiskit

Uma porta que depende de um bit medido é escrita assim:

```python
with qc.if_test((qc.clbits[1], 1)):
    qc.x(2)
```

## Nada viaja mais rápido que a luz

Sem os dois bits, Bob tem 25% de chance de cada um dos quatro estados, e essa mistura não carrega informação nenhuma sobre $|\psi\rangle$. O teletransporte depende da mensagem clássica, que viaja no máximo à velocidade da luz.

## No laboratório

A aba **Alice × Bob** compara o estado original de Alice com o estado atual de Bob. Use a linha do tempo para acompanhar o protocolo passo a passo e "Sortear de novo" para ver outros resultados de medição: com as correções certas, Bob termina igual a Alice em todos eles.
