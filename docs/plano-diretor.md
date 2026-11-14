# Quantum Learning Platform — Plano Diretor de Arquitetura e Produto

Versão revisada em 13/11/2026. Substitui o plano original e incorpora a revisão técnica feita antes do início do desenvolvimento. Onde o texto diz **[feito]**, o item já existe no repositório e é coberto por testes.

A plataforma é uma aplicação web para ensinar Computação Quântica, dos fundamentos de qubits até algoritmos e aplicações variacionais. O aluno escreve código Qiskit e vê o estado quântico mudar enquanto digita.

---

## 1. Arquitetura

### 1.1 Camadas

| Camada | Tecnologia | Responsabilidade |
| :-- | :-- | :-- |
| Interface | React + TypeScript + Three.js (React Three Fiber) + Monaco | Teoria em Markdown/LaTeX, editor, visualizações. Roda no navegador. |
| Motor | Python + Qiskit + PennyLane + NumPy + `websockets` | Roda localmente (`npm run dev`). Executa o código do aluno, simula, valida e guarda o progresso em SQLite. |

Mudanças em relação ao plano original:

- **Sem FastAPI.** O motor só fala WebSocket; a biblioteca `websockets` basta e reduz o tamanho do pacote.
- **O progresso fica no motor**, em SQLite da biblioteca padrão do Python.
- **Só web.** Houve um shell desktop (Tauri, com o motor empacotado por PyInstaller); ele foi removido: numa plataforma de estudo, o navegador basta e simplifica tudo.
- **PennyLane só entra na Fase 4.** As Trilhas 1 e 2 usam apenas Qiskit: um framework por vez para o aluno e um pacote menor. O protocolo de snapshots não depende do framework.
- **Versões fixadas** em `engine/pyproject.toml`. A API do Qiskit muda entre versões maiores e as lições dependem dela.

### 1.6 Idioma

A plataforma é só em inglês: interface (`app/src/strings.ts`), mensagens do motor (`engine/qlp_engine/messages.py`) e lições. Houve uma versão em português, inglês e alemão; ela foi removida para simplificar o trabalho enquanto o conteúdo muda. Os textos continuam centralizados, então reintroduzir idiomas depois é possível. **[feito]**

### 1.2 O ciclo em tempo real

1. **Captura (interface).** 200 ms depois da última tecla, o editor envia o código inteiro. **[feito]**
2. **Execução única com rastreamento (motor).** O código roda uma vez. Cada instrução adicionada ao circuito é registrada com a linha de nível de módulo que a originou. **[feito]**
3. **Simulação por instrução.** O motor guarda o vetor de estado depois de *cada instrução* e devolve todos os snapshots de uma vez. **[feito]**
4. **Tradução geométrica.** Para cada snapshot: amplitudes, vetor de Bloch $(x, y, z)$ e pureza de cada qubit, via estado reduzido $\rho_k = \mathrm{Tr}_{\neq k}(|\psi\rangle\langle\psi|)$. **[feito]**
5. **Navegação local.** Mover o cursor ou a linha do tempo só troca o snapshot em exibição; não há ida e volta ao motor. **[feito]**
6. **Interpolação visual.** O vetor gira sobre a esfera até o novo estado (e não em linha reta pelo centro, o que pareceria um estado misto). **[feito]**

**Por que por instrução, e não por linha.** "O estado após a linha $k$" não é bem definido quando há laços, funções ou condicionais. A regra adotada: o cursor na linha $L$ seleciona a última instrução, na ordem de execução, cuja linha de origem é $\le L$. Instruções emitidas dentro de uma função pertencem à linha que chamou a função.

**Medição no meio do circuito.** Um vetor de estado não representa "medir e seguir". O motor sorteia um ramo com gerador semeado: a mesma seed reproduz a mesma trajetória, e a interface oferece "sortear de novo". Portas condicionadas a bits clássicos (`if_test`) são executadas conforme o ramo sorteado. Estatísticas vêm de uma operação separada de *shots*, que repete trajetórias quando o circuito tem medições intermediárias. **[feito]**

**Código inválido durante a digitação.** Com debounce de 200 ms o código está quebrado boa parte do tempo. A interface mantém o último estado válido, marcado como "desatualizado", e mostra o erro na linha correspondente. **[feito]**

**Desempenho medido** (motor aquecido, nesta máquina): 0,3 ms para 1 qubit; 8 ms para 8 qubits e 23 portas, com 106 kB de resposta. O orçamento de 50 ms só se aplica à edição de código.

### 1.3 Isolamento e segurança

O modelo de ameaça real tem dois lados: código do aluno que trava ou esgota a máquina, e páginas web que tentam falar com o motor local.

| Risco | Proteção | Estado |
| :-- | :-- | :-- |
| Laço infinito | O código roda em um processo worker; passou do tempo limite (5 s), o worker é morto e outro é criado. | feito |
| Estouro de memória | Teto de qubits (10 por padrão, menor por lição) e limite de 4 GB de memória virtual no worker. | feito no Linux; no Windows e macOS vale só o teto de qubits |
| Página web conectando ao motor | WebSocket não é protegido pela same-origin policy. O motor escuta só em `127.0.0.1`, em porta aleatória, exige token por sessão e recusa origens fora da lista. | feito |
| Execuções obsoletas | Só a edição mais recente é executada; as ultrapassadas são descartadas. | feito |
| Acidentes (`open`, `input`, `import os`) | Verificação estática com lista de módulos permitidos. | feito |

A verificação estática por AST **não é uma sandbox**: é contornável e não detecta laço infinito. Ela existe para dar mensagens de erro claras. O aluno roda código próprio na própria máquina; o que precisa de cuidado no futuro é conteúdo de terceiros (lições ou arquivos de sandbox importados).

### 1.4 Convenção de ordem dos qubits

O Qiskit é little-endian: o qubit 0 é o bit menos significativo e o rótulo de um estado da base é $|q_{n-1} \dots q_1 q_0\rangle$. A plataforma adota essa convenção em todo lugar (rótulos, vetores-alvo, diagramas) e a ensina explicitamente na seção 1.5. A interface lembra a ordem sempre que há mais de um qubit. **[feito]**

### 1.5 Protocolo

Mensagens JSON com `id`; cada requisição recebe uma resposta.

| Requisição | Resposta |
| :-- | :-- |
| `catalog` | Currículo completo, com disponibilidade e progresso |
| `lesson` | Teoria, código inicial, missão, dicas (nunca a solução) |
| `run` | Passos (linha, porta, qubits) e todos os snapshots |
| `shots` | Contagens de 1024 execuções |
| `validate` | Aprovado ou não, fidelidade e mensagem de diagnóstico |
| `progress.save` | Salva código e dicas usadas |

---

## 2. A tela de estudo

### 2.1 Os cinco elementos

1. **Teoria e missão (esquerda).** Blocos curtos, intuição antes da fórmula. A missão fica fixa no rodapé do painel, sempre visível. **[feito]**
2. **Editor (centro, acima).** Monaco servido junto com a interface (funciona offline), com autocompletar das portas e descrições. **[feito]**
3. **Visualizador (direita).** Esfera de Bloch por qubit, leitura numérica $(x, y, z, |r|, \text{fase})$ e tabela de amplitudes. **[feito]** As demais visualizações entram por trilha (seção 2.3).
4. **Circuito e linha do tempo (centro, abaixo).** Diagrama gerado a partir do código; clicar em uma porta leva a visualização àquele passo. **[feito]**
5. **Barra do oráculo (rodapé).** Erros, resultado da validação e ações. **[feito]**

**Previsão antes da revelação.** Antes da missão, a lição pode perguntar o que o aluno acha que vai acontecer. Comprometer-se com uma previsão ensina mais do que só assistir à animação. **[feito]**

### 2.2 Direção visual

Sóbria e moderna, com cara de ferramenta científica: paleta neutra com um único acento azul-cobalto, painéis em cartões com cantos arredondados e sombras sutis, sem gradientes, brilhos, emojis ou vidro fosco. Tipografia IBM Plex (Sans para interface e teoria, Mono para código e números), servida junto com a interface para funcionar offline. Tema claro e escuro, seguindo o sistema por padrão. **[feito]**

A fase nunca é comunicada só por cor: todo lugar que usa a roda de cores também mostra um ponteiro e o valor do ângulo. A roda é cíclica (0 = azul, $\pi$ = laranja). Animações respeitam a preferência de movimento reduzido do sistema. **[feito]**

### 2.3 Visualizações por trilha

- **Trilha 1 (1 a 3 qubits).** Esferas de Bloch individuais (o vetor encolhe quando o qubit está emaranhado), Q-Sphere para o estado global, amplitudes com fase, comparador Alice × Bob no teletransporte. Medida de emaranhamento: concorrência só para 2 qubits; com 3 ou mais, pureza do estado reduzido.
- **Trilha 2 (3 a 8 qubits).** **[feito]**
  - **Amplitudes**: barras com sinal, cor de fase e linha tracejada da média (Deutsch-Jozsa, Bernstein-Vazirani, Grover). Mostra o estado do registrador de entrada mesmo com um qubit auxiliar, desde que este não esteja emaranhado.
  - **Fases**: um mostrador por estado da base, com probabilidade e ponteiro de fase (QFT).
  - **Registrador**: probabilidade de cada valor, rotulado também como fração (QPE e Shor). Depois que o registrador é medido, mostra o estado logo antes da medição, com um aviso.
  - **Período**: a sequência $a^x \bmod N$ com o período destacado (Shor).
- **Trilha 3.** Sliders de parâmetros, paisagem de custo 3D com trajetória do otimizador, grafo colorido (QAOA), fronteira de decisão (QNN), painel de síndromes (QEC).

Na cena 3D, todas as esferas ficam em um único canvas WebGL. **[feito]**

---

## 3. Currículo

Cada seção tem teoria, uma missão de código, uma visualização e uma regra de validação. A Trilha 3 só deve ser detalhada depois de alunos reais usarem a Trilha 1.

### Trilha 1 — Fundamentos Quânticos (iniciante)

| Seção | Missão | Visualização | Validação |
| :-- | :-- | :-- | :-- |
| **1.1 O Qubit e a Base Computacional** [feito] | Levar $|0\rangle$ a $|1\rangle$ com a porta X | Esfera de Bloch + probabilidades | Fidelidade de estado |
| **1.2 Superposição e a Porta Hadamard** [feito] | Gerador de números aleatórios: H e medição | Esfera + histograma de shots convergindo | Distribuição de contagens (não o estado, que colapsa) |
| **1.3 Fase Relativa e Rotações** [feito] | Levar $|+\rangle$ ao ponto $+Y$ do equador com S ou $R_z(\theta)$ | Esfera com cor e ponteiro de fase | Fidelidade, com diagnóstico de fase |
| **1.4 Interferência e Medição em Outras Bases** *(nova)* [feito] | Chegar a $|1\rangle$ só com H e portas de fase ($HZH = X$) | Amplitudes com sinal se cancelando | Fidelidade de estado |
| **1.5 Emaranhamento e Estados de Bell** [feito] | Construir $|\Phi^+\rangle$ com H e CNOT; convenção de ordem dos qubits | Q-Sphere + esferas colapsadas + concorrência | Fidelidade de estado |
| **1.6 Teletransporte Quântico** [feito] | Protocolo de 3 qubits com medição e correções condicionais | Comparador Alice × Bob | Estado reduzido de Bob contra vários $|\psi\rangle$ aleatórios |

A seção 1.4 é nova: o plano original prometia interferência na lição de teletransporte e não a entregava. Ela é a base da Trilha 2.

### Trilha 2 — Algoritmos Quânticos (intermediário)

| Seção | Missão | Visualização | Validação |
| :-- | :-- | :-- | :-- |
| **2.1 Phase Kickback** *(nova)* [feito] | Controle em $|+\rangle$, alvo em $|-\rangle$, CNOT: quem muda é o controle | Esferas de Bloch | Fidelidade de estado, CNOT obrigatória |
| **2.2 Algoritmo de Deutsch** *(nova)* [feito] | Uma consulta decide se $f$ de 1 bit é constante ou balanceada | Amplitudes com sinal | 4 funções secretas (2 constantes, $x$ e NOT $x$) |
| **2.3 Oráculos e Deutsch-Jozsa** [feito] | Constante ou balanceada com uma consulta (contra $2^{n-1}+1$ clássicas determinísticas) | Amplitudes com sinal | Oráculos secretos (constantes, balanceados lineares e não lineares) |
| **2.4 Bernstein-Vazirani** *(nova)* [feito] | Recuperar a string secreta de 4 bits em uma consulta | Amplitudes concentrando na resposta | 4 strings secretas |
| **2.5 Busca de Grover** [feito] | Difusor para $N = 16$, 3 iterações | Amplitudes com linha da média; 96,1% na 3ª iteração | 4 itens marcados secretos |
| **2.6 Transformada Quântica de Fourier** [feito] | QFT de 3 qubits com H, `cp` e `swap` | Fases | 5 entradas de teste, incluindo superposições com fase |
| **2.7 Estimação de Fase Quântica** [feito] | 3 qubits de contagem + 1 de autovetor; calcular `theta` com `run_shots` | Registrador | 4 fases secretas + valor de `theta` |
| **2.8 Algoritmo de Shor** [feito] | Fatorar 15 com $a = 7$: achar o período e pós-processar | Registrador (picos em 0, 4, 8, 12) e Período | Distribuição + `factors == [3, 5]` |

Shor fatora números **compostos** em primos. A exponenciação modular vem pronta no `hidden_setup.py`: o salto de QPE para Shor já é grande sem ela.

### Trilha 3 — Fronteiras e Aplicações (avançado) [feito]

Escrita em **PennyLane**; o ruído usa o dispositivo `default.mixed`. As lições de treino rodam pelo botão Executar (Ctrl+Enter), e não a cada tecla.

| Seção | Missão | Visualização | Validação |
| :-- | :-- | :-- | :-- |
| **3.1 Circuitos Variacionais** | Implementar a regra de parameter-shift e um laço de gradiente descendente | Paisagem de custo com a trajetória; convergência | Gradiente contra o do PennyLane, exatamente 2 execuções por derivada, custo ≤ −0,99, `history` verdadeiro |
| **3.2 VQE para Química Quântica** | Hartree-Fock + excitação dupla para o $H_2$ | Convergência com faixa de precisão química; curva de dissociação | Energia recalculada no estado do aluno, precisão química (1,6 mHa), só o ansatz químico |
| **3.3 QAOA e Max-Cut** | $p = 2$ camadas no grafo do curso (corte máximo 5) | Grafo com o corte mais provável; convergência; registrador | Razão de aproximação ≥ 0,85 (uma camada fica em ≈ 0,82) |
| **3.4 Redes Neurais Quânticas** | Classificador de 2 qubits e 3 camadas com data re-uploading | Fronteira de decisão; perda | Acurácia ≥ 92% num conjunto de teste que o aluno não vê |
| **3.5 Matrizes Densidade e Ruído** *(nova)* | Canal de Kraus no circuito H, T, erro, T†, H | Esfera de Bloch encolhendo; pureza | $
ho$ para três pares de probabilidades; resposta errada (30%) ≠ erro (40%) |
| **3.6 Correção de Erros Quânticos** | Código de bit flip de 3 qubits com 2 ancillas | Botões de erro; síndrome no registrador; curva de limiar | Três estados × quatro erros; fidelidade com ruído = $1 - 3p^2 + 2p^3$ |

Notas técnicas da Trilha 3:

- **VQE.** $-1{,}137$ Ha é a energia total do estado fundamental do $H_2$ na base STO-3G, não a energia de ligação. O Hamiltoniano é **pré-calculado** e distribuído como JSON (termos de Pauli por distância de ligação): calculá-lo em tempo de execução exigiria o PySCF, historicamente problemático no Windows.
- **QAOA e QNN.** Os limiares do plano original (0,85 e 92% em 50 épocas) precisam ser calibrados contra a solução de referência, com seeds fixas. Um grafo de 5 vértices pode exigir $p \ge 2$.
- **QEC.** Ruído exige simulação por matriz densidade (Aer ou canais de Kraus em NumPy). É uma dependência nova, a decidir na Fase 4.

---

## 4. O oráculo de validação

A validação compara matemática, não texto: soluções equivalentes (como $HZH$ no lugar de $X$) são aceitas.

**O alvo vem da solução de referência.** Cada lição tem um `solution.py`. O estado alvo é calculado executando esse arquivo, em vez de ser digitado no manifest. O gabarito nunca fica dessincronizado. **[feito]**

**Contra atalhos.** `allowed_gates` e `max_gates` no manifest impedem resolver qualquer missão com `qc.initialize(alvo)`; `required_gates` exige a porta que é o assunto da lição (a CNOT no phase kickback, a multiplicação modular no Shor). **[feito]**

**Variáveis.** `expected_variables` confere valores que o aluno calcula em Python depois de executar o circuito com `run_shots(qc)`, como `theta` na QPE e `factors` no Shor. **[feito]**

### Nível 1 — Estado (Trilha 1)

| Tipo | Uso | Estado |
| :-- | :-- | :-- |
| `state_fidelity` | $F = |\langle\psi_\text{alvo}|\psi_\text{aluno}\rangle|^2 \ge 0{,}999$, invariante a fase global. Se as probabilidades coincidem mas $F$ é baixo, a mensagem aponta especificamente para a fase relativa. | feito |
| `counts_distribution` | Lições com medição final (1.2): compara a distribuição dos resultados com a da solução, por distância de variação total. A distribuição é exata quando as medições são só no final; com medições intermediárias, é amostrada. | feito |
| `reduced_state` | Teletransporte (1.6): o estado de um qubit ao final, comparado com o da solução para 4 estados de entrada e 32 sorteios de medição cada. O setup oculto recebe a entrada em `_QLP_INPUT`. A regra `forbidden_pairs` proíbe portas entre os qubits de Alice e de Bob. | feito |

### Nível 2 — Vários casos secretos (Trilha 2)

| Tipo | Uso | Estado |
| :-- | :-- | :-- |
| `oracle_cases` | O circuito do aluno e a solução são executados contra vários oráculos secretos (entrada em `_QLP_INPUT`); a distribuição do registrador precisa coincidir em todos. Garante que a solução é geral e não foi escrita para um caso. Diz quantos casos passaram. | feito |
| `state_cases` | O estado final precisa coincidir com o da solução para várias entradas, incluindo superposições com fase. Equivale a conferir a operação inteira, sem exigir que o circuito seja só unitário. Substitui a fidelidade de processo prevista no plano original. | feito |

Os oráculos e helpers (`oracle`, `prepare_input`, `apply_controlled_u`, `inverse_qft`, `apply_controlled_mod_mult`) vêm do `hidden_setup.py` como portas opacas: o diagrama mostra `U_f`, `U_ω`, `QFT†`, sem revelar o conteúdo. Testes independentes conferem a física de cada lição (por exemplo, a QFT da solução contra a matriz da DFT e a multiplicação modular contra $7y \bmod 15$).

### Nível 3 — Convergência (Trilha 3)

Precisão química no VQE; razão de aproximação no QAOA; acurácia em teste na QNN. Limiares calibrados e seeds fixas.

---

## 5. Estrutura do conteúdo

```text
/content
  catalog.json                    # currículo completo, com títulos e resumos
  /schema/manifest.schema.json    # JSON Schema do manifest
  /schema/text.schema.json        # JSON Schema dos textos de cada lição
  /track_1_fundamentals
    /section_1_1_qubit
      manifest.json               # estrutura: visualizações, regras do oráculo (sem texto)
      solution.py                 # solução de referência (define o alvo)
      hidden_setup.py             # opcional: preparação oculta, oráculos
      text.json                   # título, resumo, missão, previsão, dicas
      theory.md                   # teoria em Markdown com LaTeX
      starter_code.py             # código inicial
```

Uma seção aparece como "Em breve" no mapa enquanto não tiver pasta de conteúdo. Nenhuma trilha é bloqueada: quem já sabe o básico pode ir direto ao que interessa.

**Suíte de conteúdo.** Para toda lição, os testes verificam: o manifest e os textos seguem os schemas; textos, teoria e código inicial existem; a solução de referência passa no oráculo; o código inicial executa sem passar; a resposta enviada à interface não contém a solução. **[feito]**

---

## 6. Roteiro

### Fase 1 — Fatia vertical

O objetivo é uma lição completa de ponta a ponta, não um protótipo de cada peça.

| Item | Estado |
| :-- | :-- |
| Motor: rastreamento por instrução, simulador com medição e controle clássico, shots | feito |
| Motor: worker isolado, timeout, limite de memória, WebSocket autenticado | feito |
| Oráculo Nível 1 (`state_fidelity`) e suíte de conteúdo | feito |
| Interface: mapa de trilhas, laboratório, Esfera de Bloch, amplitudes, circuito, linha do tempo, temas | feito |
| Laboratório livre (sandbox) | feito |
| Lição 1.1 completa | feito |
| CI: motor nos três sistemas e interface | escrito |

### Fase 2 — Trilha 1 completa

| Item | Estado |
| :-- | :-- |
| Validação `counts_distribution` | feito |
| Lições 1.2, 1.3 e 1.4 | feito |
| Lição 1.5: Q-Sphere e medidor de emaranhamento | feito |
| Lição 1.6: validação `reduced_state` e comparador Alice × Bob | feito |

Testar com alunos reais antes de seguir para a Trilha 2.

### Fase 3 — Trilha 2 completa e idiomas

| Item | Estado |
| :-- | :-- |
| Validadores `oracle_cases` e `state_cases`; regras `required_gates` e `expected_variables`; `run_shots` no código do aluno | feito |
| Visualizações Amplitudes, Fases, Registrador e Período | feito |
| Lições 2.1 a 2.8 | feito |
| Interface, motor e conteúdo em português, inglês e alemão | feito; depois reduzido a só inglês |

### Fase 4 — Trilha 3 e revisão com as aulas

| Item | Estado |
| :-- | :-- |
| PennyLane no motor: rastreamento de QNodes, simulação com matriz densidade e canais de Kraus | feito |
| Lições de treino: execução por botão, `analysis.py`, `check.py`, controles de experimento | feito |
| Visualizações Paisagem, Convergência, Dissociação, Grafo, Fronteira e Limiar | feito |
| Lições 3.1 a 3.6 | feito |
| Revisão das três trilhas com as aulas de Müller e de Jülich: lições novas 1.7, 2.2 e 3.5, missões e validações mais rigorosas | feito |
| Treinamento com streaming de épocas e exportação de circuitos no laboratório livre: `report(...)` envia métricas ao vivo, botão Parar, exportação em OpenQASM 2 e 3 (Qiskit e PennyLane) | feito |

As aulas de referência ficam no disco, fora do repositório (`Lecture Muller/`, `lecture (1)/`): são material de terceiros. As lições usam as ideias e os exemplos trabalhados, com texto próprio.

---

## 7. Riscos e decisões em aberto

1. **Hospedagem.** Hoje o motor roda na máquina do aluno (`npm run setup` + `npm run dev`). Para abrir a plataforma a qualquer pessoa, o motor precisa ser hospedado, com isolamento real do código do aluno (contêiner por sessão), já que a verificação estática não é uma sandbox.
2. **Limite de memória fora do Linux.** No Windows a solução é um Job Object; no macOS, o teto de qubits pode ser suficiente.
3. **Escopo.** São cerca de 15 visualizações sob medida. As Trilhas 1 e 2 são o produto; a Trilha 3 é uma expansão.
4. **Motor no navegador.** O Qiskit tem extensões nativas e não roda em Pyodide sem trabalho adicional; por isso o motor é um processo Python.
5. **Idioma.** O texto em inglês foi traduzido do português original por agentes de IA, com glossário e testes estruturais. Falta uma revisão por um falante nativo.
6. **Conteúdo de terceiros.** Lições e arquivos de sandbox importados executam código. Antes de permitir compartilhamento, é preciso um modelo de confiança.
