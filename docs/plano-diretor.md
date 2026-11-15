# Quantum Learning Platform — Plano Diretor

Versão de 15/11/2026. Descreve a plataforma como ela é hoje: o que ensina, como funciona e por que foi feita assim. O histórico de desenvolvimento está resumido no fim; os próximos passos estão no [plano de revisão](plano-de-revisao.md).

A plataforma é uma aplicação web para **uma pessoa estudar Computação Quântica sozinha**, dos números complexos até correção de erros e execução em hardware real. O estudante escreve código Qiskit ou PennyLane e vê o estado quântico mudar a cada porta, enquanto digita. Cada lição tem teoria, uma missão validada matematicamente, dicas e referências com seção e páginas exatas. Não há professores, turmas nem contas.

---

## 1. Arquitetura

### 1.1 Camadas

| Camada | Tecnologia | Responsabilidade |
| :-- | :-- | :-- |
| Interface (`app/`) | React, TypeScript, Zustand, Monaco, Three.js (React Three Fiber), KaTeX | Hub de trilhas, laboratório (teoria, editor, circuito, visualizações), páginas de referências. Roda no navegador. |
| Motor (`engine/`) | Python, Qiskit 2.6, PennyLane 0.45, NumPy, `websockets` | Executa o código do estudante num processo isolado, simula (vetor de estado e matriz densidade), valida, busca, guarda o progresso. |
| Conteúdo (`content/`) | JSON, Markdown com LaTeX, Python | Catálogo, lições, glossário, fontes. O motor carrega na inicialização. |

Decisões que moldam a arquitetura:

- **Só web.** Houve um shell desktop (Tauri, com o motor empacotado por PyInstaller); foi removido: para estudar, o navegador basta.
- **O motor não roda no navegador.** Qiskit e rustworkx (dependência do PennyLane) não têm build WebAssembly; um substituto compatível afastaria o estudante do Qiskit real. Detalhes em [decisao-motor-web.md](decisao-motor-web.md).
- **Simulador próprio.** Vetor de estado e matriz densidade em NumPy, alimentados pelas instruções do Qiskit e pelas operações de um QNode do PennyLane. Isso dá um snapshot por instrução, que é o que a interface mostra; o Qiskit Aer não é necessário.
- **Sem FastAPI.** O motor só fala WebSocket; a biblioteca `websockets` basta.
- **Versões fixadas** em `engine/pyproject.toml`: as lições dependem da API do Qiskit e do PennyLane.
- **Só inglês** na interface, nas mensagens e no conteúdo. Os textos ficam centralizados (`app/src/strings.ts`, `engine/qlp_engine/messages.py`), então outros idiomas podem voltar depois.

### 1.2 Dois modos do motor

| | Local (`npm run dev`) | Hospedado (`deploy/`) |
| :-- | :-- | :-- |
| Onde roda | Na máquina do estudante, em 127.0.0.1 | Num servidor, atrás do site (nginx faz o proxy de `/engine`) |
| Acesso | Token de sessão + lista de origens | Sem token; o Origin precisa ser o do site (`--public`) |
| Progresso | SQLite no diretório de dados do usuário | No navegador (localStorage), com exportar e importar |
| Paralelismo | Um worker | `--workers N`, com teto de conexões |
| Hardware real da IBM | Disponível (extra `engine[hardware]`) | Desligado: um servidor compartilhado não recebe chaves de terceiros |

O modo hospedado ainda não está pronto para o público: falta isolamento por sessão (gVisor ou microVM), revisão de segurança e teste de carga. Ver [deploy/README.md](../deploy/README.md).

### 1.3 O ciclo em tempo real

1. **Captura.** 200 ms depois da última tecla, a interface envia o código inteiro.
2. **Execução única com rastreamento.** O código roda uma vez; cada instrução adicionada ao circuito é registrada com a linha de nível de módulo que a originou. Num QNode do PennyLane, o rastreamento acontece dentro da função do QNode.
3. **Simulação por instrução.** O motor guarda o estado depois de cada instrução e devolve todos os snapshots de uma vez.
4. **Tradução geométrica.** Para cada snapshot: amplitudes (ou probabilidades, em estados mistos), vetor de Bloch e pureza de cada qubit, pelo estado reduzido.
5. **Navegação local.** Mover o cursor ou a linha do tempo só troca o snapshot exibido.
6. **Interpolação.** O vetor gira sobre a esfera até o novo estado.

**Por instrução, não por linha.** O cursor na linha $L$ seleciona a última instrução, na ordem de execução, cuja linha de origem é $\le L$. Instruções dentro de uma função pertencem à linha que a chamou.

**Medição no meio do circuito.** O motor sorteia um ramo com gerador semeado (a mesma seed reproduz a trajetória; "sortear de novo" troca o ramo). Portas com `if_test` seguem o ramo sorteado. Estatísticas vêm de uma operação separada de *shots*.

**Código inválido.** A interface mantém o último estado válido, marcado como desatualizado, e mostra o erro na linha.

**Treinos.** Código que chama `report(...)` (laboratório livre) e lições de treino (`live: false`) rodam só pelo botão Executar, com limite de 120 s. As métricas de `report` chegam em lotes enquanto o código roda e desenham a curva de convergência ao vivo; o botão Parar mata o worker.

**Lições sem circuito** (`framework: "python"`, Trilha 0 e algumas das Trilhas 4 e 5): o motor executa o código e devolve a tabela de variáveis numéricas do estudante no lugar do estado.

### 1.4 Isolamento e segurança

| Risco | Proteção |
| :-- | :-- |
| Laço infinito | O código roda num processo worker; passou do tempo limite (5 s, ou o da lição), o worker é morto e outro é criado. |
| Estouro de memória | Teto de qubits (10 por padrão, ajustável por lição) e limite de 4 GB de memória virtual no worker (Linux). |
| Página web falando com o motor local | Escuta só em 127.0.0.1, token por sessão, lista de origens. |
| Execuções obsoletas | Só a edição mais recente roda; as anteriores na fila são descartadas. |
| Acidentes (`open`, `input`, `import os`) | Verificação estática com lista de módulos permitidos. Não é uma sandbox: existe para dar mensagens claras. |
| Código vindo de um link de compartilhamento | Abre em modo de revisão: nada roda nem é salvo até o estudante confirmar. |
| Chave da IBM | Vai em cada requisição, fica só na memória durante a chamada, nunca é registrada nem gravada no servidor; no navegador, só se o estudante pedir. |

No modo local o estudante roda o próprio código na própria máquina. No modo hospedado o contêiner é a fronteira de segurança (usuário sem privilégios, FS somente leitura, sem capabilities, sem internet, limites de CPU, memória e PIDs).

### 1.5 Convenção de ordem dos qubits

A plataforma segue o Qiskit: qubit 0 é o bit menos significativo e o rótulo é $|q_{n-1} \dots q_1 q_0\rangle$, em todo lugar (rótulos, alvos, diagramas). Nielsen & Chuang usam a ordem inversa; as lições avisam onde isso importa (1.5, 2.3, 2.4, 2.7, 2.8) e a Trilha 0 ensina a convenção (0.4).

### 1.6 Protocolo

Mensagens JSON com `id` sobre WebSocket; cada requisição recebe uma resposta (o treino envia antes eventos `progress` com o mesmo `id`).

| Requisição | Resposta |
| :-- | :-- |
| `catalog` | Currículo, progresso, onde o progresso fica (`engine` ou `client`) e o glossário |
| `lesson` | Teoria, código inicial, objetivos, missão, dicas, desafio, referências (nunca a solução) |
| `search` | Lições que contêm todas as palavras, com trecho |
| `bibliography` | Todas as referências das lições, o material de aula e o software |
| `run` | Passos e snapshots (ou variáveis); com `train`, eventos de progresso e limite maior |
| `shots` | Contagens de 1024 execuções |
| `validate` | Aprovado ou não e a mensagem; com `challenge`, valida o desafio |
| `export` | O circuito em OpenQASM 2 ou 3 |
| `cancel` | Interrompe um treino em andamento |
| `progress.save` | Código e dicas usadas (ignorado no modo hospedado) |
| `hardware.available`, `hardware.submit`, `hardware.status` | Execução num computador quântico da IBM (só no modo local) |

---

## 2. A experiência de estudo

### 2.1 Hub

Mapa das 6 trilhas com o progresso de cada uma, a próxima lição sugerida (fora da Trilha 0, que é opcional), o laboratório livre, a página de referências e a exportação do progresso como cópia. Lições marcam desafio e projeto; trilhas concluídas ganham uma marca. A busca da barra superior (Ctrl+K) encontra lições por palavra, sem acentos e tratando hífen e traço como iguais.

### 2.2 A tela da lição

1. **Teoria (esquerda).** No topo, fixos: título, objetivos de aprendizagem, missão e dicas (uma por vez); depois da missão, o desafio opcional. Abaixo, a teoria em Markdown com LaTeX, a pergunta de previsão e as referências com seção e páginas. Os termos do glossário aparecem sublinhados, com a definição em balão.
2. **Editor (centro).** Monaco com autocompletar das portas e descrição de cada uma. Ctrl+Enter executa.
3. **Circuito (centro, abaixo).** Diagrama gerado do código; clicar numa porta (ou usar as setas) leva ao passo. O compositor escreve portas no código por cliques. Exportar em OpenQASM e, no modo local, executar no hardware da IBM.
4. **Estado (direita).** As visualizações da lição (seção 2.4), com as tabelas de vetores de Bloch e amplitudes.
5. **Barra inferior.** Erros, resultado da validação e ações (restaurar código, simular medições, executar, Check, próxima lição).

Em telas estreitas (abaixo de 1080 px), Teoria, Código e Estado viram abas. A primeira lição aberta mostra um guia de 4 passos, que reabre pelo botão "?".

### 2.3 Laboratório livre

Código Qiskit ou PennyLane sem missão, com exemplos prontos (estado de Bell, treino variacional), treino com curva ao vivo, exportação e links de compartilhamento (o código vai no fragmento da URL).

### 2.4 Visualizações

| Visualização | Uso |
| :-- | :-- |
| Esferas de Bloch | Um vetor por qubit; encolhe quando o estado do qubit é misto (emaranhamento ou ruído) |
| Q-Sphere | O estado global de até 5 qubits, com fase por cor e ponteiro |
| Comparador | Qubit de origem × qubit de destino (teletransporte, no-cloning) |
| Amplitudes | Barras com sinal, cor de fase e média (Deutsch–Jozsa, Bernstein–Vazirani, Grover) |
| Fases | Um mostrador por estado da base (QFT) |
| Registrador | Probabilidade de cada valor, também como fração (estimação de fase, Shor, códigos) |
| Período | A sequência $a^x \bmod N$ com o período (Shor) |
| Paisagem e Convergência | Custo em função dos parâmetros com a trajetória do otimizador; valor a cada passo (Trilha 3, laboratório livre) |
| Dissociação | Energia × distância entre os átomos (VQE) |
| Grafo | O corte mais provável (QAOA) |
| Fronteira de decisão | Saída do classificador no plano (3.4) |
| Limiar | Probabilidade de recuperar o estado × probabilidade de erro (4.2) |
| Variáveis | Tabela das variáveis numéricas (lições sem circuito) |

A fase nunca é comunicada só por cor: há sempre um ponteiro e o valor do ângulo.

### 2.5 Direção visual e acessibilidade

Sóbria e moderna, com cara de ferramenta científica: paleta neutra com um acento azul-cobalto, cartões com cantos arredondados e sombras sutis, sem gradientes, brilhos ou emojis. IBM Plex Sans e Mono, servidas com a interface. Tema claro e escuro.

Contraste WCAG 2.1 AA em todos os textos (verificado com axe nos dois temas), áreas roláveis e circuito acessíveis pelo teclado, passo atual anunciado a leitores de tela, descrição textual da cena 3D e respeito ao movimento reduzido.

---

## 3. Currículo

44 lições em 6 trilhas, cerca de 20 horas de estudo. Cada lição tem objetivos de aprendizagem, teoria, missão validada, 3 dicas progressivas e ao menos duas referências (um livro ou artigo e um curso ou tutorial) com o local exato de leitura. As Trilhas 1 e 2 têm desafios opcionais; cada trilha a partir da 1 termina com um projeto (rubrica de 5 ou 6 critérios). Os nomes seguem Nielsen & Chuang e os cursos da IBM Quantum Learning.

### Trilha 0: Mathematical Toolkit (optional)

| Lição | Conteúdo | Framework | Validação | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **0.1 Complex Numbers and Phases** | Complex arithmetic, modulus, polar form and the difference between global and relative phase. | Python (sem circuito) | Própria (check.py) |  |
| **0.2 Vectors and Inner Products** | Column vectors in C² and C⁴, the inner product with conjugation, normalization and the computational and ± bases. | Python (sem circuito) | Própria (check.py) |  |
| **0.3 Matrices, Unitaries and Eigenvalues** | Matrix–vector products, the conjugate transpose, unitarity, the Pauli matrices, eigenvalues and expectation values of Hermitian matrices. | Python (sem circuito) | Própria (check.py) |  |
| **0.4 Tensor Products** | The Kronecker product of vectors and matrices, product and entangled states, and Qiskit's qubit ordering. | Python (sem circuito) | Própria (check.py) |  |

### Trilha 1: Basics of Quantum Information (beginner)

| Lição | Conteúdo | Framework | Validação | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **1.1 Qubits and the Computational Basis** | State vector, normalization and the X gate on the Bloch sphere. | Qiskit | Fidelidade de estado | Desafio |
| **1.2 Superposition and the Hadamard Gate** | The states |+⟩ and |−⟩, measurement and a quantum random number generator. | Qiskit | Distribuição de medições | Desafio |
| **1.3 Relative Phase and Rotation Operators** | Z, S, T and Rz gates: same probabilities, different states. | Qiskit | Várias entradas | Desafio |
| **1.4 Interference and Measurement in Other Bases** | HH = I, HZH = X and how the relative phase decides a measurement outcome. | Qiskit | Oráculos secretos | Desafio |
| **1.5 Entanglement and the Bell States** | Tensor products, the CNOT gate, Bell states and qubit ordering. | Qiskit | Fidelidade de estado | Desafio |
| **1.6 Quantum Teleportation** | Bell pair, mid-circuit measurement and classically controlled corrections. | Qiskit | Estado reduzido por ramo | Desafio |
| **1.7 Controlled Operations** | Build the controlled-S gate from CNOT and T gates, and identities between gates. | Qiskit | Várias entradas | Desafio |
| **1.8 The No-Cloning Theorem** | No unitary operation copies an unknown quantum state; the CNOT copier works only for basis states. | Qiskit | Várias entradas | Desafio |
| **1.9 Superdense Coding** | Two classical bits travel in one qubit when sender and receiver share a Bell pair. | Qiskit | Própria (check.py) | Desafio |
| **1.10 The CHSH Game** | A shared Bell pair wins the CHSH game with probability cos²(π/8) ≈ 0.854, above the classical limit of 3/4. | Qiskit | Própria (check.py) | Desafio |
| **1.11 Project: Entanglement Swapping** | Entangle two qubits that never interacted by measuring their partners in the Bell basis. | Qiskit | Própria (check.py) | Projeto |

### Trilha 2: Fundamentals of Quantum Algorithms (intermediate)

| Lição | Conteúdo | Framework | Validação | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **2.1 Phase Kickback** | A controlled gate acting on an eigenstate of its target changes the control, not the target. | Qiskit | Fidelidade de estado | Desafio |
| **2.2 Deutsch's Algorithm** | One query decides whether a one-bit function is constant or balanced. | Qiskit | Oráculos secretos | Desafio |
| **2.3 The Deutsch–Jozsa Algorithm** | Decide constant or balanced for an n-bit function with one query. | Qiskit | Oráculos secretos | Desafio |
| **2.4 The Bernstein–Vazirani Algorithm** | Find a whole secret string with one query. | Qiskit | Oráculos secretos | Desafio |
| **2.5 Simon's Algorithm** | Recover a hidden XOR mask from outcomes that are orthogonal to it. | Qiskit | Própria (check.py) | Desafio |
| **2.6 Grover's Algorithm** | Amplitude amplification by an oracle and inversion about the mean. | Qiskit | Oráculos secretos | Desafio |
| **2.7 The Quantum Fourier Transform** | Moves the information about x from the basis states into the phases. | Qiskit | Várias entradas | Desafio |
| **2.8 Phase Estimation** | Read an eigenvalue phase with controlled powers of U and an inverse QFT. | Qiskit | Oráculos secretos | Desafio |
| **2.9 Shor's Algorithm** | Factor 15 by reducing the problem to order finding. | Qiskit | Distribuição de medições | Desafio |
| **2.10 Hamiltonian Simulation** | Approximate the evolution under a sum of terms with Trotter steps. | Qiskit | Própria (check.py) | Desafio |
| **2.11 Project: Design a Grover Oracle** | Build the oracle for a three-variable Boolean formula, then search its solutions with Grover's algorithm. | Qiskit | Própria (check.py) | Projeto |

### Trilha 3: Variational Algorithms (advanced)

| Lição | Conteúdo | Framework | Validação | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **3.1 Variational Circuits and the Parameter-Shift Rule** | Ansatz, parameter-shift gradients and gradient descent. | PennyLane | Própria (check.py) |  |
| **3.2 The Variational Quantum Eigensolver** | Ground-state energy of H₂ with a variational circuit. | PennyLane | Própria (check.py) |  |
| **3.3 QAOA for Max-Cut** | Max-Cut on a 5-vertex graph with a two-layer QAOA. | PennyLane | Própria (check.py) |  |
| **3.4 Variational Quantum Classifiers** | Classify points in the plane with two qubits and data re-uploading. | PennyLane | Própria (check.py) |  |
| **3.5 Project: A Variational Dissociation Curve** | Compute the H₂ ground-state energy with VQE at several bond lengths and locate the equilibrium distance. | PennyLane | Própria (check.py) | Projeto |

### Trilha 4: Quantum Noise and Error Correction (advanced)

| Lição | Conteúdo | Framework | Validação | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **4.1 Density Operators and Quantum Noise** | Density operators, Kraus operators, and the difference between error probability and wrong-answer probability. | PennyLane | Própria (check.py) |  |
| **4.2 The Three-Qubit Bit-Flip Code** | The three-qubit bit-flip code, syndrome measurement and the threshold. | PennyLane | Própria (check.py) |  |
| **4.3 The Three-Qubit Phase-Flip Code** | A phase flip is a bit flip in the Hadamard basis: the three-qubit phase-flip code and its X⊗X stabilizers. | PennyLane | Própria (check.py) |  |
| **4.4 The Shor Code** | Shor's nine-qubit code concatenates the phase-flip and bit-flip codes and corrects an arbitrary error on one qubit. | PennyLane | Própria (check.py) |  |
| **4.5 The Stabilizer Formalism** | Describe a code by commuting Pauli operators and read the syndrome from commutation with them. | Python (sem circuito) | Própria (check.py) |  |
| **4.6 The Toric Code** | A stabilizer code on a torus: errors are strings, syndromes are their endpoints, logical operators are loops. | Python (sem circuito) | Própria (check.py) |  |
| **4.7 The Threshold Theorem** | Concatenated codes push the logical error rate down doubly exponentially when the physical rate is below a threshold. | Python (sem circuito) | Própria (check.py) |  |
| **4.8 Project: The Shor Code Under Noise** | Build the nine-qubit Shor code, compute its logical failure probability under depolarizing noise exactly, and find the physical error rate below which encoding helps. | PennyLane | Própria (check.py) | Projeto |

### Trilha 5: Running on Quantum Hardware (advanced)

| Lição | Conteúdo | Framework | Validação | Extra |
| :-- | :-- | :-- | :-- | :-- |
| **5.1 Transpilation and Qubit Connectivity** | Basis gates, coupling maps, SWAP insertion, and why the number of two-qubit gates is the cost of a circuit on hardware. | Qiskit | Própria (check.py) |  |
| **5.2 The Qiskit Primitives** | Sampler returns counts from shots, Estimator returns expectation values of observables, and the statistical error falls as 1/√shots. | Qiskit | Própria (check.py) |  |
| **5.3 Noise on Real Devices** | T1 relaxation, T2 dephasing, readout and gate errors, and how an idle qubit loses population and coherence. | PennyLane | Própria (check.py) |  |
| **5.4 Error Mitigation** | Readout mitigation by inverting the assignment matrix and zero-noise extrapolation by folding gates, and why neither is error correction. | Python (sem circuito) | Própria (check.py) |  |
| **5.5 Project: A Mitigated Estimate on a Noisy Device** | Estimate a GHZ correlator on a noisy three-qubit device with readout mitigation and zero-noise extrapolation, and report the value with its uncertainty. | Python (sem circuito) | Própria (check.py) | Projeto |


---

## 4. O oráculo de validação

A validação compara matemática, não texto: soluções equivalentes são aceitas.

- **O alvo vem da solução de referência.** Cada lição tem um `solution.py`; o alvo é calculado executando esse arquivo.
- **Contra atalhos.** `allowed_gates`, `max_gates`, `gate_counts` e `forbidden_pairs` impedem, por exemplo, resolver com `qc.initialize(alvo)` ou ligar qubits que deveriam estar separados; `required_gates` exige a porta que é o assunto da lição.
- **Variáveis.** `expected_variables` confere valores que o estudante calcula depois de executar o circuito (com `run_shots`).
- **Casos secretos.** O setup oculto (`hidden_setup.py`) recebe cada caso em `_QLP_INPUT`: oráculos, entradas, mensagens. Os helpers aparecem no diagrama como portas opacas (`U_f`, `QFT†`).

| Tipo | Uso |
| :-- | :-- |
| `state_fidelity` | $F \ge 0{,}999$, invariante a fase global; se só a fase relativa está errada, a mensagem diz isso |
| `counts_distribution` | Distribuição das medições contra a da solução (distância de variação total) |
| `reduced_state` | Estado de um qubit ao final, para várias entradas e todos os ramos de medição (teletransporte) |
| `oracle_cases` | Distribuição de um registrador contra vários oráculos secretos |
| `state_cases` | Estado final para várias entradas, inclusive superposições com fase |
| `custom` | `check.py` da lição: `check(ns, run_case)` com mensagens próprias (treinos, lições sem circuito, desafios e projetos) |

**Desafios.** `manifest.challenge.validation` com `challenge_solution.py` (e, se preciso, `challenge_check.py` e `challenge_hidden_setup.py`). A suíte exige que a solução do desafio passe e que o código inicial e a solução da missão não passem. O progresso do desafio fica na chave `<id>:challenge`.

**Projetos.** `manifest.project: true`; a validação é uma rubrica num `check.py` que relata o primeiro critério que falha, cada um com sua mensagem.

---

## 5. Estrutura do conteúdo

```text
/content
  catalog.json                  # trilhas e lições: títulos, níveis, resumos
  glossary.json                 # termos, definição e a lição que os apresenta
  sources.json                  # material de aula e software usados no desenvolvimento
  /schema                       # JSON Schema do manifest e dos textos
  /track_N_.../section_N_M_.../
    manifest.json               # estrutura: framework, visualizações, validação, desafio, referências (sem texto)
    text.json                   # título, resumo, objetivos, missão, dicas, previsão, desafio, mensagens
    theory.md                   # teoria em Markdown com LaTeX
    starter_code.py             # código inicial
    solution.py                 # solução de referência (define o alvo)
    hidden_setup.py             # opcional: oráculos, entradas, helpers
    check.py, analysis.py       # opcionais: validação própria; dados das visualizações de treino
    challenge_*.py              # opcionais: solução, validação e setup do desafio
```

Regras de escrita em [guia-de-escrita.md](guia-de-escrita.md); referências só de [referencias-verificadas.md](referencias-verificadas.md).

**Suíte de conteúdo** (para toda lição): schemas; textos, teoria, código inicial e objetivos presentes; título igual ao do catálogo; solução passa; código inicial executa sem passar; desafio solucionável e mais difícil que a missão; referências com local verificado (sem `TODO`) e links https sem repetição; a resposta à interface não contém a solução. Há ainda testes de física independentes por trilha, testes do glossário e da bibliografia, e testes ponta a ponta no navegador (Playwright), inclusive abrindo as 44 lições.

---

## 6. Histórico

| Etapa | O que entrou |
| :-- | :-- |
| Fatia vertical | Motor com rastreamento por instrução, worker isolado, WebSocket autenticado, lição 1.1, laboratório livre |
| Trilhas 1 e 2 | Validadores de estado, distribuição, estado reduzido, oráculos e entradas; visualizações de amplitudes, fases, registrador e período |
| Trilha 3 original | PennyLane, matriz densidade e canais de Kraus, lições de treino, paisagens e convergência |
| Revisão com as aulas | Exercícios revistos com as aulas de Wegewijs e Müller (Quantum Information 2025) e de Willsch (Quantum Computing: Concepts and Algorithms, Jülich 2026) |
| Simplificação | Saem o app desktop e os idiomas português e alemão; textos reescritos (didáticos e concisos) e nomes alinhados a Nielsen & Chuang e à IBM |
| [Roadmap](roadmap.md) | CI e testes ponta a ponta, motor hospedado, Trilhas 0, 4 e 5, novas lições nas Trilhas 1 e 2, objetivos, desafios, projetos, glossário, acessibilidade, compositor, links, hardware real, página de referências |

As aulas de referência ficam no disco, fora do repositório (`Lecture Muller/`, `lecture (1)/`): são material de terceiros. As lições usam as ideias e os exemplos, com texto próprio.

---

## 7. Riscos e decisões em aberto

1. **Hospedagem pública.** Exige isolamento por sessão, revisão de segurança e teste de carga. Para uso pessoal, o modo local basta.
2. **Instalação.** O modo local pede Python e Node; um caminho só com Docker está no plano de revisão (item 2.2).
3. **Limite de memória fora do Linux.** No Windows e no macOS vale só o teto de qubits.
4. **Profundidade desigual.** A Trilha 3 é a mais curta (5 lições).
5. **Revisão humana.** 28 lições foram escritas com agentes de IA e passam nos testes de física e validação; falta uma leitura humana do ritmo didático e uma revisão do inglês por falante nativo.
6. **Dados ocultos.** O código do estudante consegue ler os casos secretos; como o estudo é individual, só prejudica quem trapaceia.
7. **CI fora do Linux.** Windows e macOS só são testados quando as branches forem enviadas ao GitHub.
