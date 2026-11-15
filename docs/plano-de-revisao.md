# Plano de revisão (novembro de 2026)

Avaliação da plataforma depois do [roadmap](roadmap.md), com o que vale modificar e em que ordem. O foco é o de sempre: **uma pessoa estudando sozinha** e fazendo os desafios (não há professores nem turmas).

Cada item traz o objetivo, o trabalho, o critério de pronto e o esforço (P ≤ 2 dias, M ≤ 1 semana, G ≤ 3 semanas).

## Retrato atual

| Aspecto | Situação |
|---|---|
| Conteúdo | 44 lições em 6 trilhas, cerca de 20 h de estudo; 20 desafios (Trilhas 1 e 2); 5 projetos; glossário de 102 termos; referências com seção e páginas |
| Profundidade por trilha | Trilha 0: 4 lições, ~1.600 palavras de teoria. Trilha 1: 11, ~4.800. Trilha 2: 11, ~4.700. **Trilha 3: 5, ~1.900**. Trilha 4: 8, ~4.500. Trilha 5: 5, ~2.200 |
| Testes | 628 do motor, 21 da interface, 18 fluxos ponta a ponta e o modo hospedado; todos passam |
| Validação mais lenta | 3.5 (5,4 s), 3.3 (1,5 s), 4.8 (1,1 s); as demais abaixo de 1 s |
| Pacote da interface | `index.js` com 4,0 MB (1,0 MB comprimido); `scene3d.js` com 0,8 MB, já carregado à parte |
| Código | `styles.css` com 2.478 linhas num arquivo só; `store.ts` com 545 linhas |
| Texto | Nenhum travessão nas teorias; um "just" em 44 lições |
| Documentação | `plano-diretor.md` reescrito em 15/11/2026; README a conferir |
| Git | As branches `trilha-3` e `roadmap` nunca passaram pela CI; Windows e macOS sem teste |

---

## Fase 1: Fechar o que existe

### 1.1 Enviar as branches e rodar a CI (P)

- **Objetivo:** validar o trabalho nos três sistemas e consolidar a `main`.
- **Trabalho:** `git push` de `trilha-3` e `roadmap` (exige o seu ok, é uma ação externa); acompanhar os jobs `engine` (Linux, Windows, macOS), `app` e `e2e`; corrigir o que falhar fora do Linux (caminhos, `resource`/limite de memória no Windows, tempo dos testes); abrir o pull request `roadmap → main` e fazer o merge.
- **Pronto quando:** a CI está verde nos três sistemas e a `main` tem a plataforma atual.

### 1.2 Documentação coerente (P)

> **Andamento:** o `plano-diretor.md` foi reescrito em 15/11/2026 (plataforma atual, 44 lições, dois modos do motor, protocolo, validação e riscos). Falta conferir o README contra o que existe.

- **Objetivo:** que os documentos descrevam a plataforma de hoje.
- **Trabalho:** reescrever o `plano-diretor.md` como "como a plataforma funciona" (arquitetura, motor, validação, conteúdo, trilhas atuais); mover o histórico de fases para uma seção curta de histórico; deixar o `roadmap.md` como registro do que foi feito; este plano como próximo passo. Conferir o README contra o que existe.
- **Pronto quando:** nenhum documento cita trilhas, ids ou recursos que não existem mais.

---

## Fase 2: Experiência de quem estuda sozinho

### 2.1 Ver a solução quando travar (M)

- **Objetivo:** hoje, depois das 3 dicas, quem continua errando não tem saída.
- **Trabalho:**
  - Depois de abrir todas as dicas e de algumas tentativas de Check sem sucesso (por exemplo, 3), aparece "Show a solution", com confirmação ("Tente de novo antes; a solução tira o desafio da lição").
  - A solução vem comentada: cada passo com uma linha explicando a ideia, não só o código. Isso exige escrever `solution_explained.md` (ou comentários na `solution.py`) para as 44 lições.
  - O progresso registra que a solução foi vista; a lição pode ser concluída mesmo assim, mas o hub mostra "concluída com solução".
  - Desafios e projetos seguem a mesma regra, com o próprio texto.
- **Pronto quando:** toda lição tem solução comentada, o botão só aparece nas condições acima e há teste ponta a ponta.

### 2.2 Começar sem instalar Python e Node (M)

- **Objetivo:** tirar a maior barreira de entrada (`npm run setup` + `npm run dev`).
- **Trabalho:**
  - Um modo local do `deploy/`: `docker compose -f deploy/local.yml up` sobe motor e interface em `http://localhost:8080`, com progresso num volume do Docker (em vez do navegador) e sem o modo público.
  - Imagem publicada (GitHub Container Registry) para quem não quer construir: `docker run -p 8080:8080 …`.
  - README com dois caminhos: "só usar" (Docker) e "desenvolver" (setup atual).
- **Pronto quando:** numa máquina só com Docker, um comando abre a plataforma e o progresso sobrevive a reiniciar o contêiner.

### 2.3 Progresso mais completo no hub (P)

- **Objetivo:** que o hub mostre o que já foi feito e quanto falta.
- **Trabalho:** contar desafios concluídos por trilha ("7/11 lições, 3/10 desafios"); tempo restante estimado por trilha (soma de `estimated_minutes` das lições não concluídas); marcar a trilha concluída com desafios incluídos de forma distinta.
- **Pronto quando:** o hub mostra lições, desafios e tempo restante por trilha.

### 2.4 Revisão ao fim de cada trilha (M)

- **Objetivo:** fixar os conceitos antes de avançar, sem depender de código.
- **Trabalho:** um questionário curto por trilha (8 a 12 perguntas de múltipla escolha com explicação), reaproveitando as previsões das lições e perguntas conceituais novas; aparece no fim da trilha e pode ser refeito; mostra quais lições revisar a partir das erradas.
- **Pronto quando:** as Trilhas 1 a 5 têm revisão, com testes de conteúdo (resposta correta existe, explicação presente, lição de origem existe).

---

## Fase 3: Conteúdo

### 3.1 Lacunas entre objetivos e missões (P)

- **Objetivo:** que cada lição cobre o que a teoria ensina.
- **Trabalho:**

  | Lição | O que a teoria ensina e a missão não cobra | Proposta |
  |---|---|---|
  | 1.1 | Normalização; coordenadas na esfera de Bloch | Previsão sobre normalizar um vetor, ou desafio que pede `theta` e `phi` de um estado |
  | 1.2 | \|−⟩ e HH = I | Desafio ou previsão com \|−⟩ e H aplicado duas vezes |
  | 1.3 | R_z (está no título e no resumo) | Missão ou desafio com `rz` e a relação R_z = e^{−iθ/2}P |
  | 1.5 | O aviso de ordem dos qubits (\|Φ⁺⟩ é simétrico e não testa isso) | Pedir um estado assimétrico, como \|01⟩ + \|10⟩ com sinal, ou um produto \|+⟩\|0⟩ |
  | 4.2 | O limiar (checado pelo controle de erro, mas fora da missão) | Mencionar o limiar na missão e nas dicas, ou tirá-lo do resumo |

- **Pronto quando:** os objetivos dessas lições incluem o tema e a validação o exercita.

### 3.2 Aprofundar a Trilha 3 (G)

- **Objetivo:** a trilha mais curta (5 lições, ~1.900 palavras) cobre pouco do curso *Variational algorithm design* da IBM.
- **Trabalho:** lições candidatas, todas com referência verificada:
  - ansätze e variational forms (expressividade, emaranhamento, número de parâmetros);
  - otimizadores (gradiente, SPSA, COBYLA) e o custo em número de avaliações;
  - barren plateaus (gradientes que somem com a profundidade; já citados na página "Optimization loops" da IBM);
  - VQE com mais de um parâmetro (por exemplo, LiH ou H₂ com ansatz geral).
- **Pronto quando:** a Trilha 3 tem pelo menos 8 lições e teoria comparável às Trilhas 1 e 2.

### 3.3 Leitura humana das lições escritas por agentes (M)

- **Objetivo:** as 28 lições novas passam nos testes (física, validação, formato), mas os testes não garantem ritmo didático nem coerência entre lições.
- **Trabalho:** ler cada trilha de ponta a ponta (você ou alguém da área), anotando saltos de dificuldade, repetições, termos usados antes de definidos e exemplos fracos; corrigir em lote por trilha.
- **Pronto quando:** cada trilha foi lida inteira e as anotações foram resolvidas.

### 3.4 Revisão do inglês (P a M)

- **Objetivo:** o texto veio de tradução e reescrita automáticas.
- **Trabalho:** revisão por falante nativo (ou leitura cuidadosa com foco em naturalidade), começando pela Trilha 1 e pela interface (`strings.ts`).
- **Pronto quando:** a Trilha 1 e a interface foram revisadas; as demais na sequência.

---

## Fase 4: Qualidade técnica

### 4.1 Carregamento mais leve (M)

- **Objetivo:** o pacote inicial de 4 MB pesa na primeira visita, principalmente no modo hospedado.
- **Trabalho:** carregar sob demanda o editor Monaco (só no laboratório), o KaTeX (só na teoria), as visualizações de treino e o compositor; medir com o relatório do build; manter o hub leve.
- **Pronto quando:** o pacote inicial fica abaixo de 1,5 MB e o hub abre sem baixar o editor.

### 4.2 Organização do código (M)

- **Objetivo:** reduzir o risco de mudanças quebrarem partes distantes (nesta sessão, substituir um bloco do `styles.css` apagou os estilos do hub).
- **Trabalho:** dividir o `styles.css` por componente (um arquivo por área: hub, laboratório, visualizações, diálogos, referências), mantendo os tokens de tema num arquivo base; dividir o `store.ts` por assunto (motor e conexão, lição e execução, progresso, desafios, hardware).
- **Pronto quando:** nenhum arquivo de estilo passa de ~400 linhas, o store está em fatias e todos os testes passam sem mudança de comportamento.

### 4.3 Dados ocultos expostos ao código do aluno (P, prioridade baixa)

- **Objetivo:** os casos secretos (`_QLP_INPUT`) e funções auxiliares do setup oculto (como o modelo de ruído da 5.5) podem ser lidos pelo próprio código do aluno.
- **Trabalho:** guardar o estado do setup oculto num fecho (closure) ou objeto sem nome acessível; o guard recusa nomes que começam com `_QLP`.
- **Pronto quando:** um teste mostra que o código do aluno não consegue ler o segredo de nenhuma lição de oráculo.
- **Nota:** como a pessoa estuda sozinha, ler o segredo só prejudica quem o faz; por isso a prioridade é baixa.

### 4.4 Teste manual com leitor de tela (P)

- **Objetivo:** a auditoria automática (axe) passa, mas não substitui o uso real.
- **Trabalho:** percorrer uma lição com NVDA (Windows) ou VoiceOver (macOS): hub, teoria, editor, circuito pelo teclado, Check, dicas e desafio.
- **Pronto quando:** os problemas encontrados estão anotados e corrigidos.

---

## Fase 5: Só se a plataforma for publicada

### 5.1 Hospedagem pública (G)

- **Objetivo:** abrir a plataforma a qualquer pessoa pela internet.
- **Trabalho:** os pendentes do [deploy/README.md](../deploy/README.md): gVisor no servidor, um sandbox por sessão (o código do aluno roda no servidor), revisão de segurança, teste de carga e limites de uso por IP.
- **Pronto quando:** a revisão de segurança passa e o teste de carga aguenta o número esperado de pessoas.
- **Nota:** para uso pessoal (local ou com o Docker do item 2.2), nada disso é necessário.

---

## Ordem recomendada

| Ordem | Item | Esforço | Por quê |
|---|---|---|---|
| 1 | 1.1 Enviar as branches e rodar a CI | P | Valida tudo o que já foi feito, nos três sistemas |
| 2 | 2.1 Ver a solução quando travar | M | É o que mais falta para quem estuda sem ajuda |
| 3 | 2.2 Começar sem instalar Python e Node | M | Tira a maior barreira de entrada |
| 4 | 3.1 Lacunas entre objetivos e missões | P | Correções concretas e pequenas |
| 5 | 4.1 Carregamento mais leve | M | Primeira impressão e modo hospedado |
| 6 | 1.2 Documentação coerente | P | |
| 7 | 2.3 Progresso mais completo no hub | P | |
| 8 | 4.2 Organização do código | M | |
| 9 | 3.2 Aprofundar a Trilha 3 | G | |
| 10 | 2.4 Revisão ao fim de cada trilha | M | |
| 11 | 3.3 Leitura humana das lições novas | M | Depende de você ou de alguém da área |
| 12 | 3.4 Revisão do inglês | P a M | Depende de um revisor |
| 13 | 4.4 Teste com leitor de tela | P | |
| 14 | 4.3 Dados ocultos | P | Prioridade baixa |
| 15 | 5.1 Hospedagem pública | G | Só se decidir publicar |
