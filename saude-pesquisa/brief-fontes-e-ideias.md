# Brief — Dados de Saúde BR: fontes verificadas + ideias de produto analítico

> Pesquisado em 2026-07-22 (Pax). Contexto: projeto semestral Análise de Dados (UFPB), dupla, ~60h, entrega 07/08/2026. Requisito: produto analítico que apoia decisão real, não análise genérica. Verificação de acesso feita HOJE via fetch direto — confiança marcada por item.

---

## PARTE 1 — Mapa de fontes com viabilidade REAL

### Achado estrutural (importante)
`opendatasus.saude.gov.br` **redireciona (302) para `dadosabertos.saude.gov.br`** — o portal migrou para um CKAN novo (Plano de Dados Abertos 2024–2026). O portal novo FUNCIONA hoje, mas a migração é exatamente o padrão INEP: URLs antigas de datasets quebram. **Mitigação: baixar tudo no dia 1 e versionar localmente.** [Confiança: Alta — verificado por fetch]

### PySUS — a peça-chave [Confiança: Alta]
- `AlertaDengue/PySUS`: **ativamente mantida — v2.7.0 em 13/07/2026**, 5 releases só em julho/2026. Verificado no GitHub releases.
- Baixa SIM, SINAN, SINASC, SIH, SIA, CNES, PNI direto do FTP do DATASUS, **converte DBC→parquet automaticamente** (resolve o problema do formato proprietário DBC). API simplificada retorna DataFrame.
- `pip install pysus`. É a via recomendada para todas as bases DATASUS abaixo.
- Red flag: depende do FTP do DATASUS; se o FTP cair, cai junto. Manutenção ativa mitiga (é a lib da Fiocruz/AlertaDengue).

### Bases, uma a uma

| Fonte | Status hoje | Formato/via | Granularidade | Confiança |
|---|---|---|---|---|
| **SIM** (mortalidade) | OK — listado no CKAN novo (CSV/API) e no FTP DATASUS via PySUS | DBC→parquet (PySUS) ou CSV | Microdado por óbito: município, causa CID-10, idade, sexo; ~1979–2023 consolidado, 2024–25 preliminar | Alta |
| **SIH/SUS** (internações) | OK via PySUS/FTP | DBC→parquet | Por AIH: município residência E internação, CID, **valor R$**, mensal, atual até ~2026 | Alta (via PySUS; não testei download real) |
| **SINAN** (agravos) | OK via PySUS/FTP; dengue/chik atuais | DBC→parquet | Por notificação, municipal | Alta |
| **SINASC** (nascidos vivos) | Suportado pelo PySUS; não localizei no CKAN novo na busca de hoje | DBC→parquet | Por nascimento, municipal | Média |
| **CNES** (estabelecimentos) | OK via PySUS; aviso oficial de instabilidade pontual no download de aplicativos SCNES (serviço "disponível e regular") | DBC→parquet; competência mensal | Por estabelecimento: leitos, equipamentos, profissionais | Alta |
| **SRAG 2019–2026** | OK — CKAN novo, **inclusive parquet** | CSV/JSON/API/**parquet** | Por hospitalização, municipal | Alta (verificado por fetch) |
| **SI-PNI / vacinação** | OK — "Doses aplicadas PNI" 2020–2026, ano a ano, no CKAN novo | CSV/API/JSON | Por dose aplicada (arquivos grandes) | Alta acesso / **Baixa qualidade**: subnotificação pós-migração e-SUS conhecida na literatura — red flag analítico |
| **ANS dados abertos** | OK — `dadosabertos.ans.gov.br/FTP/PDA/` funcionando, **atualizações de julho/2026** (NIP 05/07, beneficiários 06/07, ressarcimento 14/07) | CSV via FTP-web | Por operadora, por UF/município | Alta (verificado por fetch) |
| **TabNet** | No ar, mas o próprio DATASUS recomenda baixar bases integrais por causa de instabilidade do TabNet | Tabulação web | Agregado | Alta — **usar só para validar números, nunca como fonte primária** |
| **e-SUS Notifica** | Não verificado individualmente hoje; datasets COVID históricos existem no CKAN | CSV | Por notificação | Baixa — verificar antes de depender |
| **IBGE/PNS** | Não verificado hoje; FTP do IBGE é historicamente estável; PNS 2019 é a última edição (dado parado no tempo) | microdados TXT largura-fixa + dicionário | Amostral, UF (não municipal) | Média — pouco útil para recorte municipal |

### Red flags gerais (padrão INEP)
1. Migração de portal em andamento (opendatasus→dadosabertos) — links de tutoriais/artigos antigos vão quebrar.
2. SIM/SINAN têm defasagem: consolidado fecha com ~1,5–2 anos; usar "preliminar" exige disclaimer.
3. SI-PNI: acesso fácil, qualidade ruim (quedas de cobertura podem ser artefato de registro).
4. **Regra de ouro do projeto: semana 1 = baixar e congelar TODOS os dados localmente (parquet). Nunca depender de fonte viva na apresentação.**

---

## PARTE 2 — Ideias de produto analítico

### O que JÁ existe (para não repetir)
- **InfoGripe** (Fiocruz): nowcasting de SRAG nacional/estadual. **InfoDengue** (Fiocruz): alerta de arboviroses por cidade. **Plataforma Integrada de Vigilância** + painéis SVS do MS: monitoramento de agravos. TabNet: tabulações genéricas.
- Anti-padrão a evitar: "dashboard de casos de X por região com mapa coroplético" — já existe em todos esses.

### Ideia 1 — "Quanto custa a atenção básica que falhou" (ICSAP-PB)
- **Problema:** internações por condições sensíveis à atenção primária (hipertensão, diabetes, asma…) são falha evitável do sistema — e têm preço na AIH.
- **Decisor:** gestor municipal de saúde / COSEMS-PB — decide onde reforçar APS.
- **Fontes:** SIH/SUS via PySUS (lista ICSAP = Portaria MS 221/2008, filtro por CID). Viabilidade: Alta.
- **Ângulo não-genérico:** traduz em **R$ evitáveis por município da PB** + ranking priorizado de intervenção, não "taxa de internação por região".
- **Forma:** painel Streamlit com ranking + ficha por município. **60h: cabe bem.**
- **Riscos:** classificação ICSAP exige cuidado com CID; baixo.

### Ideia 2 — "Mapa de evasão assistencial da PB" (fluxo origem→destino)
- **Problema:** pacientes de municípios sem estrutura viajam para internar (João Pessoa/Campina Grande/Recife). Onde a regionalização falha?
- **Decisor:** Secretaria Estadual de Saúde PB (planejamento de regionalização/PPI).
- **Fontes:** SIH (município de residência vs. de internação — os dois campos existem na AIH) + CNES (leitos/serviços disponíveis). Viabilidade: Alta.
- **Ângulo:** matriz origem-destino de internações é cruzamento **pouco explorado publicamente**; nenhum painel público mostra isso por região de saúde da PB.
- **Forma:** Streamlit com mapa de fluxos + índice de dependência por região de saúde, recorte por especialidade (ex.: partos, oncologia).
- **Riscos:** junção SIH×CNES dá trabalho; escopo por 1–2 especialidades para caber em 60h. **60h: cabe com disciplina.**

### Ideia 3 — Radar de mortalidade evitável municipal
- **Problema:** que mortes um município poderia ter evitado com ação local?
- **Decisor:** gestor municipal.
- **Fontes:** SIM via PySUS + lista de causas evitáveis (MS). Viabilidade: Alta, mas dado consolidado até ~2023.
- **Ângulo:** score de evitabilidade + comparação com pares demográficos (municípios similares), não com a média estadual.
- **Riscos:** municípios pequenos = números instáveis (exige suavização/agregação trienal). **60h: cabe.**

### Ideia 4 — Monitor de recuperação vacinal (busca ativa)
- **Problema:** abandono de esquemas multidose (penta, polio); onde priorizar busca ativa?
- **Decisor:** coordenação estadual de imunização PB.
- **Fontes:** SI-PNI doses aplicadas 2020–2026 (CSV, verificado). Viabilidade acesso: Alta. **Qualidade: red flag sério** (artefatos de registro).
- **Ângulo:** taxa de abandono D1→D3 por município, não "cobertura por região".
- **Riscos:** ALTO — resultado pode medir qualidade de registro, não vacinação real. **60h: cabe, mas arriscado.**

### Ideia 5 — Termômetro de oportunidade da vigilância (data quality como produto)
- **Problema:** notificação atrasada inutiliza a vigilância. Quem digita atrasado?
- **Decisor:** núcleo estadual de vigilância epidemiológica.
- **Fontes:** SRAG 2019–2026 (parquet, verificado hoje) ou SINAN dengue — campos data-sintoma vs. data-digitação.
- **Ângulo:** InfoGripe *corrige* o atraso; ninguém publica **quem** atrasa. Meta-produto de gestão. Diferenciação máxima.
- **Riscos:** público mais nichado; a banca precisa comprar a premissa. **60h: cabe folgado.**

### Ideia 6 — Score de reclamações de planos de saúde (ANS)
- **Problema:** cidadão escolhe operadora sem dado de reclamação per capita.
- **Decisor:** cidadão / Procon-PB.
- **Fontes:** ANS NIP (atualizado 05/07/2026) + beneficiários por operadora (06/07/2026) — ambos verificados hoje. Viabilidade: Alta, e **fora do ecossistema DATASUS** (hedge contra instabilidade).
- **Ângulo:** normalizar reclamações por beneficiário, recorte NE; a ANS publica IGR agregado, mas não um comparador utilizável por UF.
- **Riscos:** juntar NIP×beneficiários por registro de operadora; médio. **60h: cabe.**

### Ideia 7 — Deserto obstétrico da PB
- **Problema:** municípios sem leito obstétrico → parto na estrada / peregrinação.
- **Decisor:** secretaria estadual (rede cegonha/regionalização).
- **Fontes:** CNES (leitos obstétricos) + SINASC (onde nasce vs. onde mora) + SIH. Viabilidade: Alta (SINASC: confiança média no CKAN, alta via PySUS).
- **Ângulo:** distância mãe-maternidade estimada + tendência de fechamento de leitos. Tema com tração social real.
- **Riscos:** 3 bases = risco de escopo; versão mínima (CNES+SINASC) cabe. **60h: apertado.**

---

## Ranking (viabilidade × diferenciação)

| # | Ideia | Viab. | Difer. | Nota |
|---|---|---|---|---|
| 1 | **Ideia 2 — Evasão assistencial O-D** | Alta | Alta | Cruzamento inédito, decisor claro, dado robusto |
| 2 | **Ideia 1 — ICSAP em R$** | Alta | Alta | Metodologia consagrada + tradução em custo; mais seguro |
| 3 | Ideia 5 — Oportunidade da vigilância | Alta | Alta | Parquet pronto; nicho |
| 4 | Ideia 6 — ANS reclamações | Alta | Média-alta | Bom plano B fora do DATASUS |
| 5 | Ideia 7 — Deserto obstétrico | Média | Alta | Escopo arriscado |
| 6 | Ideia 3 — Mortalidade evitável | Alta | Média | Defasagem do SIM |
| 7 | Ideia 4 — Vacinal | Alta | Média | Qualidade do dado compromete |

**Recomendação top 2: Ideia 2 (evasão assistencial) como principal, Ideia 1 (ICSAP em R$) como plano B/complemento** — as duas usam a MESMA base (SIH via PySUS), então a semana 1 de download/limpeza serve para ambas e a dupla pode pivotar sem perder trabalho. Esse hedge é a lição do fracasso com o INEP.

## O que NÃO consegui verificar (honestidade)
- Download real de um arquivo DBC via PySUS ponta-a-ponta (verifiquei manutenção da lib e existência das fontes, não executei). **Fazer smoke test de 1h antes de decidir.**
- Presença de SINASC e CNES no CKAN novo (existem no FTP/PySUS; confiança média no portal).
- e-SUS Notifica e PNS/IBGE: não fetchados individualmente hoje.
- Anos exatos disponíveis de SIH 2025–2026 preliminar.

## Fontes principais
- github.com/AlertaDengue/PySUS/releases (v2.7.0, 13/07/2026) · pysus.readthedocs.io
- dadosabertos.saude.gov.br (CKAN novo; SRAG 2019–2026 c/ parquet; PNI 2020–2026)
- dadosabertos.ans.gov.br/FTP/PDA/ (atualizações jul/2026)
- datasus.saude.gov.br/transferencia-de-arquivos/ · aviso de instabilidade TabNet/SCNES
- plataforma.saude.gov.br · InfoGripe/InfoDengue (Fiocruz) — concorrentes a diferenciar
