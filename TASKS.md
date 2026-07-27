# TASKS — Mapa de Evasão Assistencial da PB

> Fonte da verdade viva da EXECUÇÃO (referência do Augusto/agentes). Detalhe em `docs/backlog.md`.
> NÃO confundir com `STATUS.md` (referência leiga do Pedro — nunca sobrescrever).
> Marque [x] só quando a story passar na Definition of Done do backlog; adicione tasks novas conforme surgirem.
> **PROTOCOLO DE REVIEW (obrigatório, sem exceção):** toda story concluída passa pelo build-reviewer ANTES de qualquer checkbox. O build-reviewer é o ÚNICO que vira [x], e só com veredito APROVADO — nem o orquestrador, nem quem construiu. Autorrelato de builder não é evidência.
> Ordem: épicos P0 primeiro; dentro deles, a ordem respeita as dependências.
> Gate do backlog fechado: decisões D-1/D-2/D-3 registradas em `docs/backlog.md`.

## EP-01 — Tratamento e enriquecimento dos dados (P0 · 22–25/07)
- [x] US-01 — Base 2025 unificada com nomes de municípios (Augusto · 3 pts)
  - [x] Baixar e versionar tabela IBGE código→nome (offline após download)
  - [x] Notebook: concatenar 12 parquets, tipar, juntar nomes de origem e destino
  - [x] Validação de soma (total = Σ meses) e cobertura do join (órfãos = 0 ou justificados)
  - [x] Salvar dataset tratado em `data/processed/`
- [x] US-03 — Dicionário de dados do projeto confirmado (Augusto · 2 pts)
  - [x] Obter dicionário oficial do grupo RD (DATASUS)
  - [x] Conferir colunas ⚠️ no parquet: existência, tipo, domínios, % nulos
  - [x] Escrever dicionário de dados com veredito "usável"/"descartada" por coluna
- [x] US-02 — Região de saúde atribuída a cada internação (Augusto · 5 pts · dep: US-01)
  - [x] Validar e escolher fonte pública da malha município→região de saúde (documentar)
  - [x] Tabela código IBGE → região de saúde versionada em `data/processed/`
  - [x] Aplicar à base: região de residência e de internação (+ marca "fora da PB")
  - [x] Validações de cobertura (223 municípios) e soma; salvar base enriquecida

## EP-02 — Análise origem→destino (P0 · 25–29/07)
- [x] US-04 — Matriz O-D validada, município e região (Augusto · 5 pts · dep: US-02)
  - [x] Matriz município×município×mês + flag de evasão
  - [x] Agregação região×região×mês + taxas de evasão por origem
  - [x] Validações de soma + sanity check jan/2025 (49,8% / 20.029 — divergência do 47,8% do PRD investigada e documentada)
  - [x] Salvar agregações em `data/processed/`
- [x] US-05 — PA-1: concentração de destino (Augusto · 2 pts · dep: US-04)
  - [x] Ranking de destinos de não-residentes + % acumulado dos 2 polos
  - [x] Visualização título-afirmação em `outputs/` + veredito escrito
- [x] US-06 — PA-3: evasão × porte do município (Augusto · 3 pts · dep: US-04 · D-3: população IBGE)
  - [x] Baixar estimativa populacional IBGE mais recente por município; versionar como CSV no repo
  - [x] Taxa de evasão por município × população (faixas de porte documentadas); saldo dos polos
  - [x] Visualização + veredito
- [x] US-07 — PA-4: estabilidade temporal do fluxo (Augusto · 3 pts · dep: US-04)
  - [x] Top 20 pares O-D anuais e por mês; medida de permanência
  - [x] Visualização + veredito
- [x] US-08 — PA-5: fluxo interestadual (Augusto · 5 pts · dep: US-02 · D-1: pipeline estendido)
  - [x] Estender `src/congelar_sih.py`: baixar RD de PE/RN/CE 2025, filtrar `MUNIC_RES` na PB, salvar parquet enxuto separado em `data/raw/`
  - [x] Congelar e validar completude (12 meses × 3 UFs); `.dbc`/`.dbf` fora do git, só o parquet filtrado entra
  - [x] % interestadual + recorte de fronteira; visualização + veredito
  - ⚠️ Guard-rail (regra de decisão, não entrega): congelamento PE/RN/CE incompleto até 29/07 → PA-5 degrada p/ nota metodológica (registrar decisão)

## EP-03 — Índice de dependência por região de saúde (P0 · 28–30/07)
- [x] US-09 — Definição do índice redigida e testada (Augusto · 2 pts · dep: US-02 · D-2: fórmula fechada = % das internações de residentes da região realizadas FORA dela)
  - [x] Redigir definição: fórmula, exemplo real, interpretação leiga, limitações
  - [x] Teste de leitura com o Pedro; ajustar texto
  - ⚠️ Decisão do Augusto (24/07): o teste de leitura **deixa de ser bloqueio** para o checkbox. Julgamento dele sobre o leitor real (o Pedro é leigo em dados, não em raciocínio) — o texto foi lido e aprovado pelo Augusto. O que sustenta o [x] é a parte técnica: 12/12 números do doc recalculados do zero pela base linha a linha (RNF-05). O roteiro de 7 perguntas segue no doc e pode ser aplicado quando der, sem reabrir a story.
- [x] US-10 — Índice calculado p/ 100% das regiões + PA-2 (Augusto · 3 pts · dep: US-09, US-04)
  - [x] Índice por região + validação cruzada contra a matriz regional
  - [x] Ranking + interpretação escrita por faixa
  - [x] Veredito PA-2 + visualização; tabela em `data/processed/`

## EP-04 — Painel Streamlit (P0 · 30/07–04/08)
- [x] US-11 — Aba matriz O-D com filtros, offline e rápida (Augusto · 5 pts · dep: US-04)
  - [x] Esqueleto do app (abas) consumindo pré-agregações de `data/processed/`
  - [x] Aba matriz: filtros origem/mês; tabela legível/copiável
  - [x] Conferir números vs US-04; medir carga (<10s) e filtro (<3s)
- [ ] US-12 — Mapa interativo O-D offline (Augusto · 5 pts · dep: US-04)
  - [ ] Geojson dos municípios PB (malha IBGE) versionado em `outputs/`
  - [ ] Escolher técnica de fluxo mais simples que funcione offline no Streamlit
  - [ ] Aba com polos destacados; teste offline + teste de leitura com o Pedro
  - ⚠️ Guard-rail (regra de decisão, não entrega): >1 dia sem funcionar → degradar p/ coroplético (registrar decisão)
  - ✅ Decisão do guard-rail (25/07): mapa funcionou dentro da janela; a degradação **não** foi acionada. A cor do coroplético mudou de "taxa de evasão" para "destino principal" (área de captação) por motivo empírico — mediana da taxa de evasão municipal = 100%, 173/223 municípios > 90%, a cor não discriminava. Registro em `docs/diario-do-projeto.md` (Etapa 16).
  - ⏳ Bloqueio p/ o checkbox (build-reviewer, 25/07): critério 2 — teste de leitura com o Pedro (1 min, nomear os polos sem ajuda) segue valendo como aceite por decisão explícita da Etapa 14. Parte técnica já aprovada na revisão.
- [x] US-13 — Aba do índice de dependência (Augusto · 2 pts · dep: US-10, US-11)
  - [x] Ranking/visualização do índice + texto da definição aprovada
  - [x] Conferência dos números contra `data/processed/`
- [x] US-14 — Aba achados & recomendações (Augusto · 2 pts · dep: US-11, US-16)
  - [x] Estruturar aba com textos fechados na US-16 (fonte única: `reports/`)
  - [x] Vincular recomendação→evidência; conferir números contra notebooks

## EP-05 — Comunicação executiva & recomendações (P0 · 26/07–03/08 + 05–06/08)
- [ ] US-15 — EDA guiada sobre a base tratada (Augusto · 3 pts · dep: US-02 · Pedro usa como material de estudo)
  - [ ] Notebook-roteiro autocontido em `notebooks/90-*`, instruções leigas
  - [ ] Executar roteiro; ≥ 3 visualizações título-afirmação em `outputs/`
  - [ ] Revisão de consistência dos números
- [x] US-16 — Narrativa executiva + ≥ 3 recomendações ancoradas (Augusto · 5 pts · dep: US-05, US-06, US-07, US-10 · Pedro revisa e apresenta)
  - [x] Sumário de evidências com os números finais das PAs
  - [x] Rascunho da narrativa + recomendações em `reports/`, linguagem leiga
  - [x] Revisão cruzada com Pedro: cada recomendação ancorada em número derivável; fechar texto
- [ ] US-17 — Ensaio completo da demo offline (Dupla · 2 pts · dep: US-11..14, US-18)
  - [ ] Roteiro escrito da demo (fala, aba, filtro)
  - [ ] Ensaio cronometrado offline; ajustes; segunda passada limpa

## EP-06 — Reprodutibilidade & narrativa de atualização (P1 · 04–05/08)
- [ ] US-18 — Reprodução em máquina limpa (Augusto · 3 pts · dep: US-11)
  - [ ] Pinar dependências (requirements) com versões reais
  - [ ] Seção de execução no README p/ avaliador que nunca viu o repo
  - [ ] Teste real em ambiente limpo; corrigir o que faltar
- [ ] US-19 — Narrativa de atualização mensal documentada (Augusto · 1 pt)
  - [ ] Seção (README e/ou aba "sobre") com comando exato + nota metodológica (retificações dez)

## EP-07 — Aprofundamentos analíticos (P2 · só se sobrar hora, nunca depois de 04/08)
- [ ] US-20 — Caracterização dos maiores pares O-D (Augusto · 5 pts · dep: US-03, US-04)
  - [ ] Perfil dos top 10 pares com colunas usáveis da US-03
  - [ ] Visualização + achado escrito; propor incorporação à narrativa

---

## ⚠️ Gaps abertos (decisão humana — detalhe em docs/backlog.md)
- [x] G-4 — Formalizar troca de projeto com o professor — e-mail enviado e **aceite confirmado pelo professor em 24/07/2026**
