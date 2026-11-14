# Quantum Learning Platform

Aplicativo para aprender Computação Quântica escrevendo código Qiskit e vendo o estado quântico mudar enquanto você digita. Disponível em português, inglês e alemão.

O plano completo de arquitetura, currículo e roteiro está em [docs/plano-diretor.md](docs/plano-diretor.md).

## Estado atual

- **Três trilhas completas, 21 lições**: Fundamentos (7), Algoritmos (8, do algoritmo de Deutsch ao de Shor) e Fronteiras (6: circuitos variacionais, VQE, QAOA, redes neurais quânticas, ruído e correção de erros).
- **Qiskit nas Trilhas 1 e 2, PennyLane na Trilha 3**, com simulação de ruído por matriz densidade.
- **Exercícios revisados** a partir das aulas de Müller e de Jülich: missões, previsões e validações mais rigorosas.
- **Aplicativo desktop** (Tauri) com o motor Python embutido; também roda no navegador para desenvolvimento.
- **Visualizações**: esferas de Bloch, Q-Sphere, comparador Alice × Bob, medidor de emaranhamento, amplitudes com sinal e média, mostradores de fase, histograma de registrador e função periódica.
- **Validação matemática**: fidelidade de estado, distribuição de medições, estado reduzido, oráculos secretos e entradas de teste.
- **Interface, mensagens e conteúdo** em português, inglês e alemão; tema claro e escuro.
- **Progresso** salvo em SQLite.

Só o Linux foi testado. Windows e macOS dependem do CI, que ainda não rodou.

## Estrutura

```text
app/        Interface (React + TypeScript + Three.js + Monaco); textos em app/src/i18n/
engine/     Motor Python (Qiskit): execução, simulação, validação, progresso, mensagens
content/    Lições (manifest, solução, setup oculto, textos por idioma) e catálogo
src-tauri/  Shell desktop (Rust): abre a janela e gerencia o motor
scripts/    Utilitários de desenvolvimento
docs/       Plano diretor
```

## Pré-requisitos

- Python 3.11 ou mais novo
- Node.js 18 ou mais novo (20+ recomendado)
- Para o aplicativo desktop: Rust e, no Linux, as bibliotecas do WebKitGTK:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt install libwebkit2gtk-4.1-dev build-essential libssl-dev libayatana-appindicator3-dev librsvg2-dev
```

## Como rodar

```bash
npm run setup         # uma vez: cria engine/.venv e instala as dependências
npm run desktop:dev   # janela desktop; a interface recarrega a cada alteração
npm run dev           # alternativa no navegador: http://127.0.0.1:5173
```

`npm run dev` e `npm run desktop:dev` usam a mesma porta (5173): rode um de cada vez. O motor é carregado na inicialização, então lições novas ou alteradas só aparecem depois de reiniciar o comando.

**Use sempre `npm run desktop:*` para abrir a janela**, e não `tauri` ou o executável diretamente. O VS Code instalado via snap injeta no terminal variáveis GTK que derrubam aplicativos WebKitGTK com `symbol lookup error`; o lançador em `scripts/desktop.mjs` as restaura.

No Windows, crie o ambiente manualmente: `python -m venv engine\.venv`, `engine\.venv\Scripts\pip install -e "engine[dev]"`, `npm install` e `npm --prefix app install`.

O progresso fica no diretório de dados do usuário (`~/.local/share/quantum-learning-platform` no Linux). Para isolar uma sessão, defina `QLP_DATA_DIR=/algum/caminho`. Com `QLP_LOG=1`, o motor registra no terminal cada conexão e requisição.

## Testes

```bash
npm test             # motor (pytest) + interface (tipos e vitest)
npm run test:engine
npm run test:app
```

A suíte do motor inclui:

- **suíte de conteúdo**: em cada lição e em cada idioma, a solução passa no oráculo e o código inicial executa sem passar;
- **testes de física da Trilha 2**: resultados conferidos de forma independente das soluções;
- **testes do PennyLane**: o estado de cada QNode é comparado com o do próprio PennyLane, inclusive com ruído.

## Gerar o aplicativo

```bash
engine/.venv/bin/pip install -e "engine[package]"   # uma vez: instala o PyInstaller
npm run desktop:build                               # motor + interface + instaladores
npm run desktop:run                                 # abre o build gerado
```

Os instaladores ficam em `src-tauri/target/release/bundle/`. Para gerar só um formato: `npm run desktop:build -- --bundles deb`. Para testar só o motor empacotado: `engine/.venv/bin/python engine/packaging/smoke_test.py`.

## Criar uma lição

1. Crie `content/track_N_.../section_X_Y_nome/` com:
   - `manifest.json`: estrutura, sem texto;
   - `solution.py`;
   - opcional: `hidden_setup.py`;
   - `locales/{pt,en,de}/`, cada uma com `text.json`, `theory.md` e `starter_code.py`.

   Use uma lição existente como modelo.
2. O `id` precisa existir em `content/catalog.json`, com título e resumo nos três idiomas iguais aos de `text.json`.
3. Rode `npm run test:engine`. O alvo é calculado a partir do `solution.py`; não é preciso digitá-lo.

| Tipo de validação | Exemplo |
| :-- | :-- |
| `state_fidelity`: estado final | 1.1 |
| `counts_distribution`: estatística das medições | 1.2, 2.8 |
| `reduced_state`: estado de um qubit, para várias entradas e todos os ramos de medição | 1.6 |
| `oracle_cases`: distribuição de um registrador contra vários oráculos secretos | 2.2, 2.3, 2.5, 2.7 |
| `state_cases`: estado final para várias entradas | 2.6 |

O setup oculto recebe cada caso secreto pela variável `_QLP_INPUT`.

**Lições PennyLane** (Trilha 3) declaram `framework: "pennylane"` e qual QNode desenhar (`qnode`). Com `live: false`, o código roda pelo botão Executar. Elas podem trazer:

- um `check.py`, com validação própria e mensagens em `messages` no `text.json`;
- um `analysis.py`, que alimenta as visualizações de treino;
- `controls`, botões que passam valores ao setup oculto, como o erro injetado na 3.6.

A lição 3.6 é o exemplo mais completo.

## Como o shell e o motor conversam

O shell inicia o motor e lê a primeira linha que ele imprime: `{"event": "ready", "port": ..., "token": ...}`. A interface pede esses dados pelo comando `engine_endpoint` e abre o WebSocket. Toda mensagem leva o idioma atual (`lang`), e o motor responde nele. O shell mantém o stdin do motor aberto; se o shell morrer, o motor percebe o pipe fechado e encerra sozinho.
