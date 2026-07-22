# Backlog — Mapa de Evasão Assistencial da PB

> Fonte: docs/prd.md (aprovado). Gerado pelo scrum-master. Atualizado após o gate do backlog (decisões G-1/G-2/G-3 fechadas pelo humano).
> Projeto de ANÁLISE DE DADOS — "fatia vertical" aqui = um resultado analítico completo e verificável (dado tratado → número validado → visível/documentado), não feature de web-app.

## Definition of Done (todas as stories — barra universal pro checkbox)
- [ ] Critérios de aceite atendidos e demonstráveis (rodar o notebook/script/painel e ver o resultado)
- [ ] **Nenhum número mágico**: todo número citado é derivável de notebook/script versionado no repo (RNF-05)
- [ ] Notebook/script roda topo-a-baixo sem erro, **100% offline** (nenhuma chamada de rede em runtime — RNF-01)
- [ ] Textos executivos (painel, reports/) em pt-BR sem jargão técnico não explicado; visualizações com título-afirmação (RNF-04)
- [ ] Artefatos no lugar da arquitetura da disciplina: dados derivados em `data/processed/`, figuras/geojson em `outputs/`, textos em `reports/`
- [ ] Territórios respeitados: Augusto em `src/` + `notebooks/01-*`; Pedro em `notebooks/90-*` + `reports/`
- [ ] Commit + push ao fim da sessão (mensagem legível pelo Pedro, tom neutro)

## Definition of Ready (entrada no TASKS.md)
Uma story só é semeada quando tem: aceite Given/When/Then · dependências identificadas · regras de negócio claras · estimativa em pontos · trace ao RF/PA + épico · **executor definido (Augusto ou Pedro)**. Faltou algum → afia a story ou registra em "⚠️ Gaps para o PM"; não semeia incompleta.

## Âncora de estimativa
**US-19 (documentar a narrativa de atualização mensal) = 1 ponto.** Todas as outras são relativas a ela. Escala Fibonacci (1, 2, 3, 5, 8); nada ≥ 13 (seria épico disfarçado).

## Decisões do gate do backlog (fechadas pelo humano)
- **D-1 (ex-G-1) — PA-5 fica; pipeline será estendido.** `src/congelar_sih.py` passa a baixar RD de PE/RN/CE 2025 (12 meses cada), filtrar apenas registros com `MUNIC_RES` em municípios da PB e salvar parquet(s) enxutos separados em `data/raw/` (ex.: `sih_ufs_vizinhas_res_pb_2025.parquet`). `.dbc`/`.dbf` continuam fora do git; só o parquet filtrado entra. Executor: Augusto. → US-08.
- **D-2 (ex-G-2) — Fórmula do índice aprovada:** índice de dependência = **% das internações de residentes da região de saúde realizadas FORA dela**. Decisão fechada; US-09 só redige, exemplifica e testa a legibilidade. → US-09.
- **D-3 (ex-G-3) — Porte do município = estimativa populacional IBGE** mais recente por município, salva como CSV versionado no repo (offline). → US-06.

## ⚠️ Gaps para o PM
- **G-4 — Troca de projeto ainda não formalizada com o professor.** Ação humana; não bloqueia execução técnica, mas antecede o investimento pesado de horas.

---

## EP-01 — Tratamento e enriquecimento dos dados · P0 · janela 22–25/07 (serve: O2, O3, O5)

### US-01 — Base 2025 unificada com nomes de municípios · 3 pts · Augusto · depende de: —
**Como** analista da dupla, **quero** a base SIH-PB 2025 consolidada num único dataset com nomes de municípios legíveis **para** que toda análise seguinte fale "João Pessoa", não "250750".

**Critérios de aceite**
- **Dado** os 12 parquets congelados em `data/raw/`, **quando** rodo o notebook de tratamento, **então** sai um dataset único em `data/processed/` cuja contagem total de linhas é igual à soma das contagens dos 12 parquets de origem (validação impressa no notebook).
- **Dado** o dataset tratado, **quando** inspeciono origem e destino, **então** 100% dos códigos de `MUNIC_RES` e `MUNIC_MOV` têm nome de município atribuído (zero códigos órfãos, ou órfãos listados e explicados).

**Tasks**
- [ ] Baixar e versionar a tabela IBGE código→nome de municípios (offline após download)
- [ ] Notebook: concatenar os 12 parquets, tipar colunas-chave, juntar nomes de origem e destino
- [ ] Validação de soma (total = Σ meses) e de cobertura do join (códigos órfãos = 0 ou justificados)
- [ ] Salvar dataset tratado em `data/processed/` e registrar o passo no notebook

### US-02 — Região de saúde atribuída a cada internação · 5 pts · Augusto · depende de: US-01
**Como** gestor da SES-PB, **quero** cada internação classificada pela região de saúde de residência e de internação **para** que a análise regional (matriz por região e índice de dependência) seja possível e confiável.

**Critérios de aceite**
- **Dado** as fontes públicas candidatas (CNES/SAGE/SES-PB), **quando** valido a malha município→região de saúde, **então** a fonte escolhida e a data de referência estão documentadas no notebook, com a decisão justificada (risco apontado no PRD — validar cedo).
- **Dado** o dataset tratado, **quando** aplico o mapeamento, **então** 100% dos 223 municípios da PB têm região de saúde atribuída, e internações com destino fora da PB ficam marcadas como "fora da PB" (não nulas).
- **Dado** o dataset enriquecido, **quando** conto internações por região de residência, **então** a soma bate com o total da base (nenhum registro perdido no join).

**Tasks**
- [ ] Levantar e comparar fontes públicas da malha município→região de saúde da PB; escolher e documentar
- [ ] Construir tabela de mapeamento código IBGE → região de saúde, versionada em `data/processed/`
- [ ] Aplicar à base: colunas de região de residência e região de internação (+ marca "fora da PB")
- [ ] Validações de cobertura e de soma; salvar base enriquecida em `data/processed/`

### US-03 — Dicionário de dados do projeto confirmado · 2 pts · Augusto · depende de: —
**Como** analista da dupla, **quero** as colunas marcadas ⚠️ no PRD (`ESPEC`, `COMPLEX`, `CAR_INT`, `DIAG_PRINC`) confirmadas contra o dicionário oficial do SIH (grupo RD) e contra o parquet real **para** que o EP-07 e a caracterização dos fluxos não construam sobre coluna mal interpretada.

**Critérios de aceite**
- **Dado** o dicionário oficial do layout RD e um parquet congelado, **quando** confiro nome, tipo e domínio de cada coluna ⚠️, **então** existe uma seção de dicionário de dados no notebook (ou doc) com o domínio real observado nos dados (valores distintos + significado), e cada coluna recebe veredito "usável" ou "descartada, por quê".

**Tasks**
- [ ] Obter o dicionário oficial do grupo RD (documentação DATASUS)
- [ ] Conferir cada coluna ⚠️ no parquet: existência, tipo, valores distintos, % de nulos
- [ ] Escrever o dicionário de dados do projeto com os vereditos

---

## EP-02 — Análise origem→destino · P0 · janela 25–29/07 (serve: O2)

### US-04 — Matriz O-D validada (município e região) · 5 pts · Augusto · depende de: US-02
**Como** gestor da SES-PB, **quero** a matriz origem→destino das internações de 2025, por município e agregada por região de saúde, **para** ter a resposta numérica de "de onde vem / pra onde vai" — o produto que não existe em nenhum painel público.

**Critérios de aceite**
- **Dado** a base enriquecida, **quando** rodo o notebook da matriz, **então** a soma de todas as células da matriz município×município é igual ao total de internações da base (100% classificadas "no município" / "fora do município" — O2).
- **Dado** a matriz, **quando** agrego por região de saúde, **então** a soma da matriz regional bate com a municipal (nenhuma perda na agregação).
- **Dado** jan/2025, **quando** calculo a taxa de evasão do mês, **então** reproduzo os 47,8% / 20.029 internações citados no PRD (sanity check contra o número de referência).
- **Dado** as matrizes validadas, **quando** olho `data/processed/`, **então** as agregações estão salvas (município×município×mês e região×região×mês) prontas para consumo pelo painel.

**Tasks**
- [ ] Notebook: matriz município×município×mês + flag de evasão (residência ≠ internação)
- [ ] Agregação região×região×mês + taxas de evasão por origem
- [ ] Validações de soma (municipal = total; regional = municipal) e sanity check jan/2025
- [ ] Salvar agregações em `data/processed/`

### US-05 — PA-1 respondida: concentração de destino · 2 pts · Augusto · depende de: US-04
**Como** professor, **quero** a resposta à PA-1 (para onde vão os que se internam fora?) com veredito explícito da hipótese **para** ver análise consolidada no formato pergunta→evidência→conclusão.

**Critérios de aceite**
- **Dado** a matriz O-D, **quando** rodo a seção PA-1 do notebook, **então** sai o ranking de destinos das internações de não-residentes, o % concentrado por João Pessoa + Campina Grande, e um veredito escrito ("hipótese confirmada/refutada: X%") com uma visualização de título-afirmação.

**Tasks**
- [ ] Ranking de destinos de não-residentes + % acumulado dos 2 polos
- [ ] Visualização com título-afirmação (salvar em `outputs/`)
- [ ] Parágrafo de veredito no notebook (insumo da US-16)

### US-06 — PA-3 respondida: evasão × porte do município · 3 pts · Augusto · depende de: US-04
**Como** gestor da SES-PB, **quero** saber se a taxa de evasão cai com o porte do município **para** entender se o problema é estrutural dos municípios pequenos.

> Decisão D-3 (gate — fechada): porte = **estimativa populacional IBGE** mais recente por município, salva como CSV versionado no repo (offline).

**Critérios de aceite**
- **Dado** o CSV de população IBGE versionado no repo, **quando** rodo a seção PA-3, **então** cada município da PB tem taxa de evasão e população atribuídas (100% de cobertura do join), com visualização da relação evasão×porte e veredito escrito da hipótese (inclusive a checagem "polos com evasão < 10% e importadores líquidos").

**Tasks**
- [ ] Baixar a estimativa populacional IBGE mais recente por município e versionar como CSV no repo
- [ ] Taxa de evasão por município de residência + cruzamento com população (faixas de porte documentadas)
- [ ] Saldo importador/exportador dos polos; visualização + veredito

### US-07 — PA-4 respondida: estabilidade temporal do fluxo · 3 pts · Augusto · depende de: US-04
**Como** gestor da SES-PB, **quero** saber se os grandes fluxos O-D são estáveis mês a mês **para** sustentar que a evasão é estrutural (problema de pactuação), não circunstancial.

**Critérios de aceite**
- **Dado** a matriz mensal, **quando** rodo a seção PA-4, **então** vejo os 20 maiores pares O-D do ano e uma medida de permanência deles mês a mês (ex.: em quantos dos 12 meses cada par fica no top 20), com visualização e veredito escrito.

**Tasks**
- [ ] Top 20 pares O-D anuais e por mês; medida de permanência
- [ ] Visualização da estabilidade + veredito no notebook

### US-08 — PA-5 respondida: fluxo interestadual · 5 pts · Augusto · depende de: US-02
**Como** gestor da SES-PB, **quero** dimensionar quanto da evasão sai da PB (residentes internados em PE/RN/CE) **para** fundamentar pactuação interestadual nas regiões de fronteira.

> Decisão D-1 (gate — fechada): o pipeline será estendido. Os arquivos RD são por UF do estabelecimento, então residentes PB internados fora estão nos RD de PE/RN/CE — congela-se apenas o recorte filtrado.

**Critérios de aceite**
- **Dado** o pipeline estendido, **quando** rodo `src/congelar_sih.py` para PE/RN/CE 2025, **então** os 12 meses de cada UF são baixados, filtrados para apenas registros com `MUNIC_RES` em municípios da PB, e salvos como parquet(s) enxutos separados em `data/raw/` (ex.: `sih_ufs_vizinhas_res_pb_2025.parquet`), com placar de completude por UF×mês; `.dbc`/`.dbf` ficam fora do git — só o parquet filtrado entra.
- **Dado** os dados interestaduais congelados, **quando** rodo a seção PA-5, **então** sai o % da evasão total que é interestadual, o recorte por região de saúde de fronteira, e o veredito da hipótese (< 15%, concentrada na fronteira), com visualização.

**Tasks**
- [ ] Estender `src/congelar_sih.py`: baixar RD de PE/RN/CE 2025, filtrar `MUNIC_RES` na PB, salvar parquet enxuto separado em `data/raw/`
- [ ] Rodar o congelamento e validar completude (12 meses × 3 UFs); conferir `.gitignore` (`.dbc`/`.dbf` fora, parquet filtrado dentro)
- [ ] Análise: % interestadual da evasão total, recorte por região de fronteira, visualização + veredito

---

## EP-03 — Índice de dependência por região de saúde · P0 · janela 28–30/07 (serve: O3)

### US-09 — Definição do índice redigida e testada · 2 pts · Augusto · depende de: US-02
**Como** gestor da SES-PB, **quero** a definição escrita do índice de dependência (fórmula + interpretação) que eu entenda em uma leitura **para** confiar no número-assinatura do produto.

> Decisão D-2 (gate — fechada): índice de dependência = **% das internações de residentes da região de saúde realizadas FORA dela**. A fórmula não está mais em aberto — esta story só redige, exemplifica e testa a legibilidade.

**Critérios de aceite**
- **Dado** a fórmula aprovada (D-2), **quando** redijo a definição, **então** existe um texto com: fórmula, exemplo numérico com uma região real, interpretação em linguagem leiga e limitações declaradas (AIH ≠ paciente único, reinternações) — pronto para ser exibido tal-qual no painel (RF-02).
- **Dado** a definição, **quando** um leitor leigo (Pedro) a lê, **então** ele consegue explicar com as próprias palavras o que o número significa (teste real com o Pedro).

**Tasks**
- [ ] Redigir a definição: fórmula, exemplo numérico com uma região real, interpretação leiga, limitações
- [ ] Teste de leitura com o Pedro; ajustar o texto

### US-10 — Índice calculado para 100% das regiões + PA-2 · 3 pts · Augusto · depende de: US-09, US-04
**Como** gestor da SES-PB, **quero** o índice calculado para todas as regiões de saúde da PB, com interpretação escrita, **para** ler um número por região e entender quanto ela depende de fora (PA-2 respondida).

**Critérios de aceite**
- **Dado** a fórmula aprovada, **quando** rodo o notebook do índice, **então** 100% das regiões de saúde da PB têm índice calculado, com validação: o índice recalculado a partir da matriz regional (US-04) bate com o calculado da base linha a linha.
- **Dado** os índices, **quando** rodo a seção PA-2, **então** sai a contagem de regiões com índice > 50% e o veredito escrito da hipótese ("≥ 1/3 das regiões"), com visualização de título-afirmação.

**Tasks**
- [ ] Notebook: índice por região + validação cruzada contra a matriz regional
- [ ] Ranking das regiões + interpretação escrita por faixa
- [ ] Veredito PA-2 + visualização; salvar tabela do índice em `data/processed/`

---

## EP-04 — Painel Streamlit · P0 · janela 30/07–04/08 (serve: O1, O2, O3)

### US-11 — Aba matriz O-D com filtros, offline e rápida · 5 pts · Augusto · depende de: US-04
**Como** gestor da SES-PB, **quero** consultar a matriz O-D filtrando por município/região de origem e por mês **para** dimensionar a pactuação com números (RF-01, RF-08).

**Critérios de aceite**
- **Dado** o repo clonado e a rede **desligada**, **quando** rodo `streamlit run`, **então** o painel abre em < 10s com a aba da matriz funcional (RNF-01, RNF-02).
- **Dado** a aba aberta, **quando** aplico qualquer filtro (município, região, mês), **então** a resposta vem em < 3s (consome pré-agregações de `data/processed/`, nunca cálculo bruto por interação).
- **Dado** um filtro aplicado, **quando** olho a tabela, **então** os totais exibidos batem com a matriz validada da US-04, e a tabela é legível/copiável para citação (RF-08).

**Tasks**
- [ ] Esqueleto do app Streamlit (estrutura de abas) carregando pré-agregações de `data/processed/`
- [ ] Aba matriz: filtros de origem (município/região) e mês; tabela legível/copiável
- [ ] Conferência de números contra a US-04; medir tempos de carga e filtro

### US-12 — Mapa interativo O-D offline · 5 pts · Augusto · depende de: US-04
**Como** jornalista de dados, **quero** ver os fluxos de evasão num mapa interativo da PB com os polos destacados **para** encontrar e comunicar padrões que não existem em painel público (RF-03).

**Critérios de aceite**
- **Dado** a rede desligada, **quando** abro a aba do mapa, **então** o mapa da PB renderiza a partir de geojson versionado localmente em `outputs/` (zero tile/CDN externo).
- **Dado** o mapa, **quando** um leigo o observa por até 1 minuto, **então** identifica sem ajuda os polos concentradores (João Pessoa e Campina Grande destacados) — teste real com o Pedro.
- **Guard-rail anti-sumidouro:** **dado** 1 dia de trabalho na aba, **quando** o mapa ainda não estiver funcional, **então** degradar para a visualização mais simples que comunique o fluxo (ex.: mapa coroplético de evasão por origem) — decisão registrada, sem estourar a janela.

**Tasks**
- [ ] Obter e versionar geojson dos municípios da PB (malha IBGE) em `outputs/`
- [ ] Escolher a técnica de visualização de fluxo mais simples que funcione offline no Streamlit
- [ ] Implementar a aba com destaque dos polos; teste offline + teste de leitura com o Pedro

### US-13 — Aba do índice de dependência · 2 pts · Augusto · depende de: US-10, US-11
**Como** gestor da SES-PB, **quero** ver o índice de cada região com a definição da métrica no próprio painel **para** entender o número sem ajuda externa (RF-02).

**Critérios de aceite**
- **Dado** a aba aberta, **quando** olho uma região, **então** vejo o índice, sua posição no ranking e a definição redigida na US-09 acessível no mesmo lugar (texto tal-qual aprovado).
- **Dado** os números exibidos, **quando** confiro contra a tabela da US-10, **então** batem exatamente.

**Tasks**
- [ ] Aba: ranking/visualização do índice por região + texto da definição
- [ ] Conferência dos números contra `data/processed/`

### US-14 — Aba achados & recomendações · 2 pts · Augusto · depende de: US-11, US-16
**Como** professor, **quero** ler no painel as respostas às perguntas analíticas e as recomendações em linguagem executiva **para** avaliar análise consolidada e comunicação na própria demo (RF-04, RF-05).

**Critérios de aceite**
- **Dado** a aba aberta, **quando** leio cada achado, **então** ele segue o formato achado + número + implicação, e cada recomendação aponta explicitamente a evidência (número/visualização) que a sustenta.
- **Dado** qualquer número da aba, **quando** procuro sua origem, **então** ele existe em um notebook/script versionado (RNF-05 — nenhum número digitado à mão).

**Tasks**
- [ ] Estruturar a aba com os textos fechados na US-16 (fonte única: `reports/`)
- [ ] Vincular cada recomendação à sua evidência; conferir números contra os notebooks

---

## EP-05 — Comunicação executiva & recomendações · P0 · janela 26/07–03/08 + 05–06/08 (serve: O4, O1)

### US-15 — EDA guiada do Pedro sobre a base tratada · 3 pts · **Pedro** (guiado) · depende de: US-02
**Como** membro não-técnico da dupla, **quero** explorar a base tratada em notebooks do meu território com um roteiro pronto **para** produzir os gráficos de apoio da apresentação e me apropriar dos dados.

**Critérios de aceite**
- **Dado** a base tratada em `data/processed/` e um notebook-roteiro em `notebooks/90-*` (células com instruções em linguagem leiga, preparado pelo Augusto), **quando** o Pedro executa as células no Jupyter e preenche as partes indicadas, **então** o notebook roda topo-a-baixo e produz ≥ 3 visualizações com título-afirmação salvas em `outputs/`.
- **Dado** o notebook do Pedro, **quando** o Augusto o revisa, **então** nenhum número contradiz os notebooks técnicos (mesma base, mesmos totais).

**Tasks**
- [ ] (Augusto) Preparar notebook-roteiro autocontido em `notebooks/90-*` com instruções leigas
- [ ] (Pedro) Executar o roteiro, escolher e refinar ≥ 3 visualizações, salvar em `outputs/`
- [ ] (Augusto) Revisão de consistência dos números

### US-16 — Narrativa executiva + ≥ 3 recomendações ancoradas · 5 pts · **Pedro** (guiado, com a dupla) · depende de: US-05, US-06, US-07, US-10
**Como** gestor da SES-PB, **quero** uma narrativa do achado central e ≥ 3 recomendações práticas, cada uma ancorada num número da análise, **para** saber o que fazer a respeito da evasão (O4).

**Critérios de aceite**
- **Dado** os vereditos das PAs, **quando** leio o texto em `reports/`, **então** existe uma narrativa do achado central + ≥ 3 recomendações, e cada recomendação cita o número exato e o notebook de onde ele vem (nenhuma recomendação sem evidência apontável).
- **Dado** o texto, **quando** um leitor leigo o lê, **então** não encontra jargão sem explicação (RNF-04) — é o mesmo texto que abastece a aba do painel (US-14).

**Tasks**
- [ ] (Augusto) Compilar os vereditos das PAs num sumário de evidências com os números finais
- [ ] (Pedro) Rascunhar narrativa + recomendações em `reports/`, em linguagem leiga
- [ ] (Dupla) Revisão cruzada: cada recomendação ancorada em número derivável; fechar o texto

### US-17 — Ensaio completo da demo offline · 2 pts · Dupla · depende de: US-11, US-12, US-13, US-14, US-18
**Como** dupla, **quero** ensaiar a demo completa com a rede desligada, cronometrada, **para** que no dia 07/08 nada dependa de sorte (O1).

**Critérios de aceite**
- **Dado** o notebook da apresentação com rede desligada, **quando** executamos o roteiro da demo do zero (`streamlit run` → navegação → achado principal), **então** tudo funciona, o achado principal aparece em < 1 min de interação (intento do EP-04) e o roteiro escrito da fala está em `reports/`.
- **Dado** o ensaio, **quando** algo falha ou trava, **então** vira item corrigido antes de 06/08 (janela de folga do plano).

**Tasks**
- [ ] Roteiro escrito da demo (quem fala o quê, qual aba, qual filtro)
- [ ] Ensaio cronometrado offline; lista de ajustes; segunda passada limpa

---

## EP-06 — Reprodutibilidade & narrativa de atualização · P1 · janela 04–05/08 (serve: O5, O1)

### US-18 — Reprodução em máquina limpa · 3 pts · Augusto · depende de: US-11 (painel mínimo existente)
**Como** professor, **quero** clonar o repo numa máquina limpa e ver o painel rodar sem tocar no DATASUS **para** comprovar a reprodutibilidade (RF-06, RNF-03).

**Critérios de aceite**
- **Dado** uma máquina/ambiente limpo, **quando** sigo apenas a seção de execução do README (`git clone` → install das dependências pinadas → `streamlit run`), **então** o painel abre completo, sem nenhum download do DATASUS e sem passo não documentado.
- **Dado** o repo, **quando** confiro o versionamento, **então** os parquets necessários estão no git e `.dbc`/`.dbf` estão fora (regra fixa do projeto).

**Tasks**
- [ ] Pinar dependências (requirements) com as versões reais do ambiente
- [ ] Escrever a seção de execução do README para avaliador que nunca viu o repo
- [ ] Teste real em ambiente limpo (venv novo ou segunda máquina); corrigir o que faltar

### US-19 — Narrativa de atualização mensal documentada · 1 pt · Augusto · depende de: — **(âncora = 1 pt)**
**Como** professor, **quero** entender como um mês novo do DATASUS entra no produto com um comando **para** aceitar a "viabilidade real" como demonstrada (RF-07).

**Critérios de aceite**
- **Dado** o README/painel, **quando** leio a seção de atualização, **então** entendo em linguagem leiga o ciclo: DATASUS publica lote mensal (~2 meses de atraso) → `src/congelar_sih.py` congela o mês → o painel passa a exibi-lo — incluindo o comando exato e a nota metodológica sobre retificações de dezembro.

**Tasks**
- [ ] Escrever a seção (README e/ou aba "sobre" do painel) com o comando e a nota metodológica

---

## EP-07 — Aprofundamentos analíticos · P2 · sem janela reservada — só se sobrar hora, nunca depois de 04/08 (serve: O2, O4)

### US-20 — Caracterização dos maiores pares O-D · 5 pts · Augusto · depende de: US-03, US-04
**Como** gestor da SES-PB, **quero** saber **o que** motiva os maiores fluxos (diagnóstico, especialidade, complexidade, caráter da internação) **para** enriquecer as recomendações com um segundo eixo.

**Critérios de aceite**
- **Dado** as colunas aprovadas no dicionário (US-03), **quando** rodo o notebook de caracterização, **então** cada um dos top 10 pares O-D tem um perfil (principais capítulos CID-10 e/ou especialidade/complexidade/caráter), com ≥ 1 achado adicional escrito em formato achado + número + implicação.
- **Dado** o achado adicional, **quando** ele é forte, **então** entra como recomendação extra na US-16/US-14 sem retrabalho estrutural (mesmo formato).

**Tasks**
- [ ] Perfil dos top 10 pares com as colunas usáveis da US-03
- [ ] Visualização + achado escrito; propor incorporação à narrativa se couber

---

## Ordem de execução sugerida (respeita dependências e janelas do PRD)
US-01 → US-03 → US-02 → US-04 → (US-05, US-07 em paralelo com US-15) → US-09 → US-06 → US-10 → US-08 → US-11 → US-12 → US-13 → US-16 → US-14 → US-18 → US-19 → US-17 → [US-20 só se sobrar hora].

**Total: 20 stories · 66 pontos (61 sem o EP-07).**
