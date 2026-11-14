# Quantum Learning Platform

Plataforma web para aprender Computação Quântica escrevendo código Qiskit e vendo o estado quântico mudar enquanto você digita. A interface e as lições estão em inglês.

O plano completo de arquitetura, currículo e roteiro está em [docs/plano-diretor.md](docs/plano-diretor.md).

## Estado atual

- **Três trilhas completas, 21 lições**: Fundamentos (7), Algoritmos (8, do algoritmo de Deutsch ao de Shor) e Fronteiras (6: circuitos variacionais, VQE, QAOA, redes neurais quânticas, ruído e correção de erros).
- **Qiskit nas Trilhas 1 e 2, PennyLane na Trilha 3**, com simulação de ruído por matriz densidade.
- **Exercícios revisados** a partir das aulas de Müller e de Jülich: missões, previsões e validações mais rigorosas.
- **Roda no navegador**, com o motor Python local (WebSocket em 127.0.0.1).
- **Visualizações**: esferas de Bloch, Q-Sphere, comparador Alice × Bob, medidor de emaranhamento, amplitudes com sinal e média, mostradores de fase, histograma de registrador e função periódica.
- **Validação matemática**: fidelidade de estado, distribuição de medições, estado reduzido, oráculos secretos e entradas de teste.
- **Interface, mensagens e conteúdo em inglês**; tema claro e escuro.
- **Progresso** salvo em SQLite.

Só o Linux foi testado. Windows e macOS dependem do CI.

## Estrutura

```text
app/        Interface (React + TypeScript + Three.js + Monaco); textos em app/src/strings.ts
engine/     Motor Python (Qiskit): execução, simulação, validação, progresso, mensagens
content/    Lições (manifest, textos, teoria, código inicial, solução, setup oculto) e catálogo
scripts/    dev.mjs: sobe o motor e a interface juntos
docs/       Plano diretor
```

## Pré-requisitos

- Python 3.11 ou mais novo
- Node.js 18 ou mais novo (20+ recomendado)

## Como rodar

```bash
npm run setup   # uma vez: cria engine/.venv e instala as dependências
npm run dev     # motor + interface; abra http://localhost:5173
```

A interface recarrega a cada alteração. O motor carrega as lições na inicialização, então lições novas ou alteradas só aparecem depois de reiniciar o `npm run dev`.

No Windows, crie o ambiente manualmente: `python -m venv engine\.venv`, `engine\.venv\Scripts\pip install -e "engine[dev]"`, `npm install` e `npm --prefix app install`.

O progresso fica no diretório de dados do usuário (`~/.local/share/quantum-learning-platform` no Linux). Para isolar uma sessão, defina `QLP_DATA_DIR=/algum/caminho`. Com `QLP_LOG=1`, o motor registra no terminal cada conexão e requisição.

## Publicar na web

A versão web roda o motor num servidor, atrás do site (`deploy/`): `SITE_ORIGIN=https://… docker compose -f deploy/docker-compose.yml up --build`. Leia [deploy/README.md](deploy/README.md) antes: o código dos alunos roda no servidor, e o que falta para abrir ao público está listado lá. O motivo de não rodar no navegador está em [docs/decisao-motor-web.md](docs/decisao-motor-web.md).

## Testes

```bash
npm test             # motor (pytest) + interface (tipos e vitest)
npm run test:engine
npm run test:app
npm run test:e2e     # ponta a ponta (Playwright, usa o Chrome do sistema)
```

A suíte do motor inclui:

- **suíte de conteúdo**: em cada lição, a solução passa no oráculo e o código inicial executa sem passar;
- **testes de física da Trilha 2**: resultados conferidos de forma independente das soluções;
- **testes do PennyLane**: o estado de cada QNode é comparado com o do próprio PennyLane, inclusive com ruído.

## Criar uma lição

1. Crie `content/track_N_.../section_X_Y_nome/` com:

   - `manifest.json`: estrutura, sem texto;
   - `solution.py`;
   - opcional: `hidden_setup.py`;
   - `text.json`, `theory.md` e `starter_code.py`.

   Use uma lição existente como modelo.

   O texto segue o [guia de escrita](docs/guia-de-escrita.md). As referências (`references` no manifest) indicam onde ler com precisão em `location`: seção, título e páginas de um livro (Nielsen & Chuang, 10ª edição de aniversário; Griffiths & Schroeter, 3ª edição) ou aula e seção de um curso da IBM.
2. O `id` precisa existir em `content/catalog.json`, com título e resumo iguais aos de `text.json`.
3. Rode `npm run test:engine`. O alvo é calculado a partir do `solution.py`; não é preciso digitá-lo.

| Tipo de validação                                                                        | Exemplo            |
| :----------------------------------------------------------------------------------------- | :----------------- |
| `state_fidelity`: estado final                                                           | 1.1                |
| `counts_distribution`: estatística das medições                                       | 1.2, 2.8           |
| `reduced_state`: estado de um qubit, para várias entradas e todos os ramos de medição | 1.6                |
| `oracle_cases`: distribuição de um registrador contra vários oráculos secretos       | 2.2, 2.3, 2.5, 2.7 |
| `state_cases`: estado final para várias entradas                                        | 2.6                |

O setup oculto recebe cada caso secreto pela variável `_QLP_INPUT`.

**Lições PennyLane** (Trilha 3) declaram `framework: "pennylane"` e qual QNode desenhar (`qnode`). Com `live: false`, o código roda pelo botão Executar. Elas podem trazer:

- um `check.py`, com validação própria e mensagens em `messages` no `text.json`;
- um `analysis.py`, que alimenta as visualizações de treino;
- `controls`, botões que passam valores ao setup oculto, como o erro injetado na 4.2.

A lição 4.2 (código de bit flip) é o exemplo mais completo.

## Como a interface e o motor conversam

O `npm run dev` inicia o motor (`python -m qlp_engine`) numa porta fixa (8765) com um token de sessão, e o Vite passa esses dados à interface (`VITE_ENGINE_PORT`, `VITE_ENGINE_TOKEN`). A interface abre um WebSocket em `ws://127.0.0.1:8765`; o motor só aceita conexões com o token certo e vindas das origens permitidas (`--allow-origin`). O código do aluno roda num processo separado, com limite de tempo e de memória.
