# Quantum Learning Platform — Plano Diretor de Arquitetura e Produto

Versão revisada em 13/11/2026. Substitui o plano original e incorpora a revisão técnica feita antes do início do desenvolvimento. Onde o texto diz **[feito]**, o item já existe no repositório e é coberto por testes.

A plataforma é um aplicativo desktop para ensinar Computação Quântica, dos fundamentos de qubits até algoritmos e aplicações variacionais. O aluno escreve código Qiskit e vê o estado quântico mudar enquanto digita.

---

## 1. Arquitetura

### 1.1 Camadas

| Camada | Tecnologia | Responsabilidade |
| :-- | :-- | :-- |
| Shell desktop | Tauri (Rust) | Janela e ciclo de vida do sidecar. Permanece fino: inicia o motor (e o reinicia se cair), lê a porta e o token que ele imprime e os entrega à interface. Mantém o stdin do motor aberto: se o shell morrer, o motor encerra sozinho. **[feito]** |
| Interface | React + TypeScript + Three.js (React Three Fiber) + Monaco | Teoria em Markdown/LaTeX, editor, visualizações. Não depende do Tauri: roda igual no navegador durante o desenvolvimento, o que mantém aberta a porta para uma versão web. |
| Motor (sidecar) | Python + Qiskit + NumPy + `websockets` | Executa o código do aluno, simula, valida e guarda o progresso em SQLite. Empacotado com PyInstaller. |

Mudanças em relação ao plano original:

- **Sem FastAPI.** O motor só fala WebSocket; a biblioteca `websockets` basta e reduz o tamanho do pacote.
- **O progresso fica no motor**, em SQLite da biblioteca padrão do Python, e não no Rust. Funciona igual com ou sem o shell.
- **PennyLane só entra na Fase 4.** As Trilhas 1 e 2 usam apenas Qiskit: um framework por vez para o aluno e um pacote menor. O protocolo de snapshots não depende do framework.
- **Versões fixadas** em `engine/pyproject.toml`. A API do Qiskit muda entre versões maiores e as lições dependem dela.

### 1.6 Idiomas

A plataforma funciona em português, inglês e alemão. **[feito]**

- **Interface**: dicionários em `app/src/i18n/{pt,en,de}.ts`. O de português define as chaves; o TypeScript recusa o build se faltar alguma tradução. O idioma vem da escolha salva, senão do sistema, senão inglês, e pode ser trocado pela barra superior a qualquer momento.
- **Motor**: mensagens em `engine/qlp_engine/i18n.py`. Cada requisição leva o idioma, e erros, diagnósticos de validação e textos de conteúdo voltam nele.
- **Conteúdo**: cada lição tem `locales/{pt,en,de}/` com textos, teoria e código inicial. Código e identificadores (`prepare_alice_state`, `oracle`, `run_shots`) são os mesmos nos três idiomas; só os comentários mudam.
- **Troca no meio de uma lição**: textos e mensagens mudam na hora. O código do aluno é preservado; se ainda for o código inicial intocado, ele é trocado pelo do novo idioma.
- **Testes**: a suíte de conteúdo exige os três idiomas em toda lição, o mesmo número de dicas e opções, título igual ao do catálogo e o código inicial de cada idioma executando sem resolver a missão.

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
2. **Editor (centro, acima).** Monaco empacotado no aplicativo (funciona offline), com autocompletar das portas e descrições em português. **[feito]**
3. **Visualizador (direita).** Esfera de Bloch por qubit, leitura numérica $(x, y, z, |r|, \text{fase})$ e tabela de amplitudes. **[feito]** As demais visualizações entram por trilha (seção 2.3).
4. **Circuito e linha do tempo (centro, abaixo).** Diagrama gerado a partir do código; clicar em uma porta leva a visualização àquele passo. **[feito]**
5. **Barra do oráculo (rodapé).** Erros, resultado da validação e ações. **[feito]**

**Previsão antes da revelação.** Antes da missão, a lição pode perguntar o que o aluno acha que vai acontecer. Comprometer-se com uma previsão ensina mais do que só assistir à animação. **[feito]**

### 2.2 Direção visual

Sóbria e moderna, com cara de ferramenta científica: paleta neutra com um único acento azul-cobalto, painéis em cartões com cantos arredondados e sombras sutis, sem gradientes, brilhos, emojis ou vidro fosco. Tipografia IBM Plex (Sans para interface e teoria, Mono para código e números), empacotada no aplicativo para funcionar offline. Tema claro e escuro, seguindo o sistema por padrão. **[feito]**

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

### Trilha 3 — Fronteiras e Aplicações (avançado)

| Seção | Missão | Visualização | Validação |
| :-- | :-- | :-- | :-- |
| **3.1 Circuitos Variacionais** | Ansatz hardware-efficient; regra de parameter-shift na prática | Sliders de parâmetros + $\langle Z \rangle$ | Fidelidade para parâmetros dados |
| **3.2 VQE para Química Quântica** | Energia do estado fundamental do $H_2$ | Curva de dissociação + paisagem de custo | $|E - E_\text{exato}| \le 1{,}6 \times 10^{-3}$ Ha |
| **3.3 QAOA e Max-Cut** | Camadas de custo ($R_{ZZ}$) e mistura ($R_X$), grafo de 5 vértices | Grafo colorido + histograma | Razão de aproximação (limiar a calibrar) |
| **3.4 Redes Neurais Quânticas** | Classificador com data re-uploading para círculos concêntricos | Fronteira de decisão | Acurácia em teste (limiar a calibrar) |
| **3.5 Ruído e Correção de Erros** | Código de repetição de 3 qubits com 2 ancillas | Injeção de erro + painel de síndromes | Estado lógico recuperado para cada erro injetado |

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
  catalog.json                    # currículo completo, com títulos e resumos nos três idiomas
  /schema/manifest.schema.json    # JSON Schema do manifest
  /schema/text.schema.json        # JSON Schema dos textos de cada idioma
  /track_1_fundamentals
    /section_1_1_qubit
      manifest.json               # estrutura: visualizações, regras do oráculo (sem texto)
      solution.py                 # solução de referência (define o alvo)
      hidden_setup.py             # opcional: preparação oculta, oráculos
      /locales/{pt,en,de}
        text.json                 # título, resumo, missão, previsão, dicas
        theory.md                 # teoria em Markdown com LaTeX
        starter_code.py           # código inicial (comentários no idioma)
```

Uma seção aparece como "Em breve" no mapa enquanto não tiver pasta de conteúdo. Nenhuma trilha é bloqueada: quem já sabe o básico pode ir direto ao que interessa.

**Suíte de conteúdo.** Para toda lição, os testes verificam: o manifest e os textos seguem os schemas; os três idiomas existem e têm a mesma estrutura; a solução de referência passa no oráculo; o código inicial de cada idioma executa sem passar; a resposta enviada à interface não contém a solução. **[feito]**

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
| Empacotamento do motor (PyInstaller onedir) com teste de fumaça | feito no Linux (217 MB; pronto em 0,1 s) |
| Shell Tauri com o motor embutido | feito no Linux (executável de 9 MB; `.deb` de 104 MB) |
| CI nos três sistemas, incluindo instaladores | escrito, ainda não executado |

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
| Interface, motor e conteúdo em português, inglês e alemão | feito |

### Fase 4 — Trilha 3

Decisão sobre PennyLane e sobre simulação com ruído; treinamento com streaming de épocas; visualizações variacionais; seções 3.1 a 3.5; exportação de circuitos no laboratório livre.

---

## 7. Riscos e decisões em aberto

1. **Distribuição.** Continua sendo o maior risco. No Linux o instalador `.deb` tem 104 MB e funciona. Faltam validar: Windows e macOS, AppImage, assinatura de código e falsos positivos de antivírus.
2. **Limite de memória fora do Linux.** No Windows a solução é um Job Object; no macOS, o teto de qubits pode ser suficiente.
3. **Escopo.** São cerca de 15 visualizações sob medida. As Trilhas 1 e 2 são o produto; a Trilha 3 é uma expansão.
4. **Versão web.** A interface já roda em navegador. O que impede uma versão web é o motor: o Qiskit tem extensões nativas e não roda em Pyodide sem trabalho adicional. Alternativa a avaliar: motor hospedado.
5. **Idiomas.** Inglês e alemão foram traduzidos a partir do português por agentes de IA, com glossário e testes estruturais. Os testes garantem estrutura, não qualidade: falta uma revisão por falantes nativos, principalmente da terminologia em alemão. As mensagens de falha do shell desktop (ex.: motor não encontrado) ainda estão só em português.
6. **Conteúdo de terceiros.** Lições e arquivos de sandbox importados executam código. Antes de permitir compartilhamento, é preciso um modelo de confiança.
