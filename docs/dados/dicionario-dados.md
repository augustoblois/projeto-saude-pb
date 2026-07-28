# Dicionário de dados — SIH/DATASUS grupo RD (base tratada 2025)

> US-03 do backlog. Base auditada: `data/processed/sih_pb_2025_tratado.parquet` — 258.125 linhas, 118 colunas, 100% referente a AIH de residentes/atendidos na PB em 2025.
> Auditoria empírica rodada em 2026-07-23 (ver `Read/Bash` no histórico da sessão — não há script versionado no repo, é output de uma sessão exploratória de agente).

## Fonte do dicionário oficial — CONFIRMADA

Duas fontes primárias do DATASUS, baixadas via FTP (`ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/`) em 2026-07-23:
- **`docs/IT_SIHSUS_1603.pdf`** (Informe Técnico do SIH-SUS) — define nome, tipo e significado de cada campo do layout RD. Versionado neste repo.
- **`Auxiliar/TAB_SIH.zip → CNV/LEITOS.CNV`** (tabela de conversão oficial, atualizada 2026-07-21) — domínio completo de códigos de `ESPEC`. Não versionada (5,8 MB); os códigos relevantes estão transcritos abaixo.

As definições de campo abaixo foram conferidas contra o IT_SIHSUS; o domínio de `ESPEC` contra o LEITOS.CNV (que corrigiu 3 códigos da versão preliminar deste doc: 09, 10 e 87).

## Como a auditoria foi feita

Script Python (pandas) rodado sobre o parquet tratado, coluna a coluna: dtype real, % de nulos (`NaN` real do parquet) e % de "string vazia" (sentinela usado pelo SIH pra ausência de valor, diferente de nulo), contagem de valores distintos, `value_counts` (top valores) para colunas categóricas, e min/max/média via conversão numérica para colunas de alta cardinalidade. Nenhum arquivo do projeto foi alterado; script ficou no scratchpad da sessão, não versionado no repo (regra da tarefa).

## Sumário executivo

- **118 colunas totais.** Vereditos: **~46 usáveis** (informação real, domínio válido) · **~72 descartadas** (constantes, vazias, ou fora do escopo O-D/perfil deste projeto).
- As **4 colunas ⚠️ do PRD estão confirmadas usáveis**: `ESPEC`, `COMPLEX`, `CAR_INT`, `DIAG_PRINC` — domínio observado bate com o esperado, nulos = 0%.
- **Colunas mais relevantes pra US-20** (perfil dos maiores pares O-D): `DIAG_PRINC` (diagnóstico), `ESPEC` (especialidade do leito), `COMPLEX` (complexidade), `CAR_INT` (caráter eletivo/urgência), `IDADE`+`COD_IDADE` (perfil etário), `UTI_MES_TO`/`UTI_INT_TO`/`MARCA_UTI` (uso de UTI), `VAL_TOT` (valor pago), `MORTE` (óbito), `DIAS_PERM` (tempo de permanência). Todas confirmadas usáveis, 0% nulos.
- **Achado extra de auditoria:** ~55 colunas do layout RD (UTI_MES_IN/AN/AL, UTI_INT_IN/AN/AL, VAL_SADT/RN/ACOMP/ORTP/SANGUE/SADTSR/TRANSP/OBSANG/PED1AC, DIAG_SECUN, NATUREZA, RUBRICA, NUM_PROC, TOT_PT_SP, CPF_AUT, SEQ_AIH5, CBOR, CNAER, VINCPREV, GESTOR_DT, INFEHOSP, CID_ASSO, CID_MORTE, DIAGSEC2-9/TPDISEC2-9 quase vazias) são **constantes ou >99% vazias** nesta base — não trazem informação para o escopo do projeto. Isso é normal: são campos do layout nacional usados por outras esferas (ex.: RN=recém-nascido, campos zerados quando não se aplica ao caso).

---

## 1. Colunas ⚠️ do PRD (auditoria detalhada)

### `ESPEC` — Especialidade do leito
- **Significado oficial:** código do tipo de leito/especialidade em que o paciente foi internado.
- **Tipo:** string de 2 dígitos (`char(2)`, conf. IT_SIHSUS campo 4). **Domínio oficial** (LEITOS.CNV): 01-Cirúrgico, 02-Obstétricos, 03-Clínico, 04-Crônicos, 05-Psiquiatria, 06-Pneumologia Sanitária (Tisiologia), 07-Pediátricos, 08-Reabilitação, 09-Leito Dia/Cirúrgicos, 10-Leito Dia/Aids, 87-Saúde Mental (Clínico). *(Códigos 09/10/87 conferidos contra o CNV oficial em 2026-07-23 — a versão preliminar deste doc os descrevia errado.)*
- **Domínio observado:** 10 valores distintos, 0% nulos. Concentração em `01` (36,81%), `03` (31,69%), `02` (16,39%), `07` (12,28%); cauda longa em `05`,`87`,`06`,`09`,`10`,`04` (< 2% cada). Bate com o esperado (cirurgia/clínica médica/obstetrícia/pediatria dominam internações gerais).
- **VEREDITO: usável.** Domínio consistente, zero nulos, granularidade suficiente pra perfil de especialidade nos top pares O-D (US-20).

### `COMPLEX` — Complexidade do procedimento
- **Significado oficial:** nível de complexidade assistencial do procedimento realizado (atenção básica / média / alta complexidade).
- **Tipo:** string de 2 dígitos. **Domínio esperado:** 01-Atenção básica, 02-Média complexidade, 03-Alta complexidade.
- **Domínio observado:** apenas 2 valores — `02` (90,46%) e `03` (9,54%); `01` não aparece. 0% nulos.
- **Interpretação:** ausência de `01` é esperada — internação hospitalar (grupo RD) por definição não cobre atenção básica; o dado bate com a expectativa.
- **VEREDITO: usável.** Ótimo eixo pra caracterizar quais pares O-D concentram alta complexidade (evasão pra alta complexidade é achado forte pra US-20).

### `CAR_INT` — Caráter da internação
- **Significado oficial:** natureza da internação. **Domínio esperado:** 01-Eletiva, 02-Urgência, 03-Acidente no trabalho, 04-Acidente de trajeto, 05-Outros acidentes de trânsito, 06-Outros.
- **Domínio observado:** 4 valores — `02` Urgência (74,64%), `01` Eletiva (25,33%), `06` (0,01%), `05` (0,01%). 0% nulos.
- **VEREDITO: usável.** Domínio bate 100% com o esperado. Eixo direto pra "os pares O-D grandes são majoritariamente urgência ou eletiva?" (relevante pro achado de evasão — urgência sugere problema estrutural de oferta local, eletiva sugere escolha).

### `DIAG_PRINC` — Diagnóstico principal (CID-10)
- **Significado oficial:** código CID-10 (4 caracteres, letra + 3 dígitos, sem ponto) do diagnóstico principal que motivou a internação.
- **Tipo:** string, formato CID-10. 0% nulos, 5.256 valores distintos (esperado — CID-10 tem milhares de subcategorias).
- **Domínio observado:** valores bem formados (`O800`, `J189`, `Z302`, `N390`, `O689`, `I64`...) — todos no padrão CID-10 válido, capítulos plausíveis pra perfil de internação (O=gravidez/parto, J=respiratório, N=genito-urinário, I=circulatório). Top código `O800` (parto único espontâneo) = 3,84% — consistente com obstetrícia sendo a maior fatia de internações no SUS.
- **VEREDITO: usável.** Fonte primária pra perfil de diagnóstico dos pares O-D (US-20); recomenda-se agregar por capítulo CID-10 (primeira letra) pra evitar dispersão em 5 mil categorias.

---

## 2. Outras colunas relevantes pra US-20 (perfil dos pares O-D)

| Coluna | Significado | Domínio observado | Nulos | Veredito |
|---|---|---|---|---|
| `IDADE` | Idade do paciente (na unidade de `COD_IDADE`) | numérico, min 0 – max 99, média 41,55 | 0% | **Usável** — perfil etário dos pares O-D |
| `COD_IDADE` | Unidade da idade (4=anos, 2/3=dias/meses, 5=?) | 4 valores; 94,55% código `4` (anos) | 0% | **Usável, com ressalva** — cruzar com `IDADE` só faz sentido pro subconjunto `COD_IDADE=4`; os ~5,4% em outra unidade (provável neonatal) precisam de tratamento à parte pra não distorcer médias de idade |
| `DIAS_PERM` | Dias de permanência da internação | numérico, min 0 – max 281, média 5,30 | 0% | **Usável** — tempo de internação por par O-D |
| `MORTE` | Indicador de óbito | binário 0/1; 5,03% óbito | 0% | **Usável** — taxa de óbito por par O-D (proxy de gravidade) |
| `UTI_MES_TO` / `UTI_INT_TO` | Total de dias de UTI (no mês / na internação) | numérico 0–90 / 0–100, médias 0,58 / 0,07 (a maioria não usa UTI) | 0% | **Usável** — proporção de casos com UTI por par O-D |
| `MARCA_UTI` | Tipo de UTI utilizada | 14 valores; 91,26% `00` (sem UTI) | 0% | **Usável** — complementa UTI_MES_TO/UTI_INT_TO |
| `VAL_TOT` | Valor total pago pela AIH | numérico, min 0 – max 262.028,17, média 2.120,99 | 0% | **Usável** — valor médio por par O-D (custo da evasão) |
| `VAL_UTI` | Valor pago referente à UTI | numérico 0 – 58.800, média 366,99 | 0% | **Usável, complementar** a VAL_TOT |
| `MUNIC_RES` / `MUNIC_MOV` | Código IBGE do município de residência / de internação | numéricos válidos (faixa IBGE), já resolvidos em `nome_mun_res`/`nome_mun_mov` na US-01 | 0% | **Usável** — já é a base da matriz O-D (US-01/US-04) |
| `nome_mun_res` / `nome_mun_mov` | Nome do município (join US-01) | 555 / 62 valores distintos; concentração em João Pessoa/Campina Grande em ambos os lados | 0% | **Usável** — confirma que o join da US-01 não deixou órfãos |
| `uf_res` / `uf_mov` | UF de residência / de internação | `uf_res` tem 26 valores (99,42% PB, resto interestadual — sinaliza pra fora); `uf_mov` é constante `PB` (base é só-PB, por enquanto) | 0% | **Usável** — `uf_res` já mostra o recorte interestadual que a US-08 vai aprofundar; `uf_mov` será não-constante só depois que o pipeline incluir PE/RN/CE (US-08) |

---

## 3. Colunas administrativas/metadados (fora do escopo O-D, mas com informação real)

Confirmadas usáveis para eventuais análises secundárias, mas **não fazem parte do escopo O-D/US-20** deste projeto: `UF_ZI`, `ANO_CMPT`, `MES_CMPT` (chave temporal, já usada), `CGC_HOSP`/`CNPJ_MANT`/`CNES` (identificação do estabelecimento — 31,19%/29,70% vazios respectivamente, resto preenchido), `N_AIH` (chave única da AIH, 255.809 de 258.125 distintos — atenção, sugere ~2.316 AIHs com número repetido, possivelmente prorrogações; não investigado nesta auditoria), `SEXO`, `RACA_COR`, `NAT_JUR`, `GESTAO`, `FINANC`, `FAEC_TP` (85,50% vazio — só preenchido pra procedimentos custeados por FAEC), `REGCT`, `NACIONAL`, `GESTOR_*`, `REMESSA`, `SEQUENCIA`.

`FONTE_ORC` é a única coluna com **nulo real de parquet** (15,31% `NaN`, não string vazia) — vale investigar se é falha de tratamento na US-01 ou ausência legítima no dado fonte antes de usar em qualquer análise (não usada no escopo O-D atual, então não bloqueia).

---

## 4. Colunas descartadas (constantes ou >99% vazias nesta base)

**Motivo em todos os casos: 100% de um único valor (constante) ou string vazia dominante — zero variância, zero informação pra este escopo.**

- **Constantes em 0/vazio** (não se aplica ao recorte PB/2025 do grupo RD): `UTI_MES_IN`, `UTI_MES_AN`, `UTI_MES_AL`, `UTI_INT_IN`, `UTI_INT_AN`, `UTI_INT_AL`, `VAL_SADT`, `VAL_RN`, `VAL_ACOMP`, `VAL_ORTP`, `VAL_SANGUE`, `VAL_SADTSR`, `VAL_TRANSP`, `VAL_OBSANG`, `VAL_PED1AC`, `DIAG_SECUN` (superado por `DIAGSEC1..9`), `NATUREZA`, `RUBRICA`, `NUM_PROC`, `TOT_PT_SP`, `CPF_AUT`, `SEQ_AIH5`, `CBOR`, `CNAER`, `VINCPREV`, `GESTOR_DT`, `INFEHOSP`, `CID_ASSO`, `CID_MORTE`, `uf_mov` (constante só até a US-08 estender pra PE/RN/CE).
- **>99% vazias/irrelevantes pro escopo:** `DIAGSEC2` a `DIAGSEC9` e `TPDISEC2` a `TPDISEC9` (diagnósticos secundários adicionais — só o 1º secundário (`DIAGSEC1`, 85,84% vazio) tem alguma massa, e mesmo assim fora do escopo do diagnóstico principal usado na US-20), `CID_NOTIF` (97,07% vazio — notificação compulsória, não se aplica à maioria), `AUD_JUST`/`SIS_JUST` (texto livre, >99% vazio), `ETNIA` (99,74% código genérico `0000`), `CONTRACEP1`/`CONTRACEP2`/`GESTRISCO`/`INSC_PN` (aplicável só a obstetrícia, quase sempre `0`/vazio no total da base), `HOMONIMO`, `NUM_FILHOS`, `INSTRU`, `IND_VDRL`, `MARCA_UCI`, `VAL_UCI`, `VAL_SH_FED`/`VAL_SP_FED`/`VAL_SH_GES`/`VAL_SP_GES` (componentes de repasse financeiro, fora do escopo analítico do projeto), `IDENT` (99,03% AIH normal — pouca variância útil).

---

## Observação metodológica final

Todas as colunas listadas como "usável" têm **0% de nulos reais** na base tratada — os "buracos" de informação nesta base são majoritariamente por **string vazia** (sentinela do layout RD pra "não se aplica"), não por falha de tratamento da US-01. Recomenda-se, ao usar qualquer coluna do grupo 4 acima em notebook analítico, tratar a string vazia como categoria própria ("não se aplica"), não descartá-la como se fosse nulo verdadeiro.
