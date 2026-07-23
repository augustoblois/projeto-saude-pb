# Diário do projeto — linha do tempo pra apresentação

> Guia cronológico do que foi feito, por quê, e onde está. Escrito pro Augusto-daqui-a-2-semanas
> que esqueceu os detalhes: é a base do roteiro da apresentação (07/08/2026).
> Regra: ≤ 10 linhas por etapa; detalhe mora nos arquivos apontados em ONDE.
> Atualizar a cada story fechada (faz parte do ritual de fim de sessão).

---

## Etapa 1 — Escolha do tema e pesquisa de fontes (meados de julho/2026)
**O QUE:** Abandonamos o projeto anterior (ENEM) por depender de cruzamento de dados individuais sensíveis. Pesquisamos fontes públicas de saúde e ranqueamos 7 ideias de projeto; venceu o **mapa de evasão assistencial da PB**: descobrir de onde saem e pra onde vão os pacientes internados fora do próprio município.
**POR QUÊ:** O critério de escolha foi "anti-genérico": essa matriz origem→destino não existe em nenhum painel público, e interessa diretamente à Secretaria Estadual de Saúde (decisões de regionalização).
**ONDE:** `../saude-pesquisa/brief-fontes-e-ideias.md`

## Etapa 2 — Congelamento dos dados (SIH/DATASUS)
**O QUE:** Baixamos os 12 meses de 2025 do SIH (Sistema de Informações Hospitalares — registra toda internação paga pelo SUS) direto do FTP do DATASUS, com o script `src/congelar_sih.py`. Os arquivos originais (formato `.dbc`) foram convertidos pra parquet (formato de dados pronto pra análise) e versionados no repositório: ~258 mil internações da PB.
**POR QUÊ:** Regra nº 1 do projeto: nada na apresentação depende de fonte viva — se o site do DATASUS cair no dia, tanto faz. Tentamos a API de conveniência do PySUS antes; não servia (instável), por isso o FTP direto.
**ONDE:** `src/congelar_sih.py`, `data/raw/*.parquet`

## Etapa 3 — Organização do trabalho (governança com IA)
**O QUE:** Antes de codar, estruturamos o projeto com um fluxo de gestão assistido por IA (Project Conduction): entrevista de briefing → PRD (documento de requisitos) → backlog com 20 histórias de usuário e critérios de aceite → auditoria de qualidade. Cada história tem pontos de esforço, dependências e prazo.
**POR QUÊ:** Projeto de ~60h com dois integrantes e data fixa: sem um plano fatiado e priorizado, a chance de chegar em 07/08 com metade pronta era alta. O backlog também define o que fica de fora (tão importante quanto o que entra).
**ONDE:** `docs/briefing.md`, `docs/prd.md`, `docs/backlog.md`, `TASKS.md`

## Etapa 4 — US-01: base 2025 unificada com nomes de municípios ✅
**O QUE:** Juntamos os 12 arquivos mensais num único dataset e traduzimos os códigos IBGE de município (residência e internação) para nomes legíveis, usando tabela oficial do IBGE baixada e versionada. Validações: o total de internações da base unificada é igual à soma dos 12 meses (nada se perdeu) e nenhum código ficou sem nome (zero "órfãos").
**POR QUÊ:** Toda a análise origem→destino depende de saber, por internação, o município de residência e o de atendimento — com nome, não código. As validações garantem que a base tratada é fiel à congelada.
**ONDE:** `notebooks/01-*`, `data/processed/sih_pb_2025_tratado.parquet`

## Etapa 5 — US-03: dicionário de dados ✅
**O QUE:** Auditamos as 118 colunas da base: o que cada uma significa (layout oficial do SIH), o que ela contém de verdade (tipo, valores, % de vazios), e um veredito por coluna — **usável** ou **descartada**. Resultado: ~46 usáveis / ~72 descartadas (a maioria das descartadas é campo do layout nacional que vem vazio no nosso recorte). As 4 colunas críticas pro perfil dos fluxos (`ESPEC`, `COMPLEX`, `CAR_INT`, `DIAG_PRINC`) foram confirmadas usáveis, 0% nulos.
**POR QUÊ:** Documentação oficial ≠ realidade do dado: usar uma coluna sem checar seu conteúdo real é o jeito clássico de construir análise sobre areia. O dicionário protege as análises futuras (especialmente a caracterização dos maiores fluxos).
Conferimos tudo contra as fontes oficiais do DATASUS (informe técnico em PDF + tabela de códigos), baixadas por FTP — a conferência corrigiu 3 códigos de especialidade que estavam descritos errado na primeira versão.
**ONDE:** `docs/dicionario-dados.md`, `docs/IT_SIHSUS_1603.pdf`

## Etapa 6 — US-02: região de saúde em cada internação ✅
**O QUE:** Atribuímos a cada uma das 258.125 internações a região de saúde de residência (`regiao_res`) e a de internação (`regiao_int`), usando a base territorial oficial do DATASUS (`ftp.datasus.gov.br/territorio/tabelas/2025/10-base_territorial_out25.zip`, baixada em 23/07/2026) — a mesma relação município→região que o TabWin do Ministério usa. Residentes de outros estados (1.502 internações, maioria PE/RN) marcados "Fora da PB".
**POR QUÊ:** A matriz O-D e o índice de dependência — o produto do projeto — são por região de saúde (16 na PB), a unidade de planejamento da Secretaria. Validações: 223 municípios cobertos, 1 região cada; zero linhas perdidas; zero nulos. Primeiro retrato: região de João Pessoa 41,3% + Campina Grande 26,4% ≈ ⅔ das internações do estado. Aprovado em revisão independente que refez as contas do zero.
**ONDE:** `notebooks/01-regiao-saude.ipynb`, `src/baixar_base_territorial.py`, `data/processed/regioes_saude_pb.csv`, `data/processed/sih_pb_2025_regioes.parquet`

## Etapa 7 — US-04: matriz origem→destino ✅
**O QUE:** Construímos a matriz O-D: internações contadas por (município residência × município internação × mês) e por (região × região × mês), com flag de evasão e taxas de evasão por região de origem. Validação-âncora jan/2025: volume bateu exato (20.029); a taxa recalculada deu **49,8%, não os 47,8% do PRD** — investigamos 5 variantes de cálculo (inclusive a pegadinha `UF_ZI` do SIH), nenhuma reproduz o número antigo (fase de pesquisa, sem código rastreável), e **adotamos 49,8%** — corrigido em PRD/briefing/backlog. Ano fechado: evasão municipal 50,5%; extremos regionais 1,8% (região de JP) vs 84,5% (3ª região); top fluxo Santa Rita→JP (5.645).
**POR QUÊ:** A matriz é o coração do produto — análises PA-1..PA-4, índice de dependência e painel consomem essas agregações, não a base linha-a-linha. Aprovada em revisão independente que refez todas as contas do zero.
**ONDE:** `notebooks/01-matriz-od.ipynb` (§4 = investigação da divergência), `data/processed/matriz_od_municipal_mensal.parquet`, `matriz_od_regional_mensal.csv`, `taxas_evasao_regional.csv`

## Etapa 8 — US-08 (parte 1): paraibanos internados fora do estado ✅ (congelamento)
**O QUE:** Estendemos o pipeline (`src/congelar_sih_vizinhos.py`) pra baixar os 12 meses de 2025 de PE/RN/CE (~1,9 mi de internações), filtrar residentes da PB e congelar um parquet enxuto: **3.682 internações** (PE 2.147, RN 1.359, CE 176). Validado: 36/36 arquivos, 100% residentes PB, 12 meses sem buracos.
**POR QUÊ:** Os arquivos do SIH são organizados pela UF do hospital — paraibano internado em Recife está no arquivo de PE. Sem esse passo, a evasão interestadual (PA-5) seria invisível. Achado preliminar: volume ~1,4% do interno → a evasão da PB é quase toda dentro do estado. Falta a parte 2: análise PA-5 (% e recorte de fronteira).
**ONDE:** `src/congelar_sih_vizinhos.py`, `data/raw/sih_pb_residentes_fora_2025.parquet`

---

*Próximas etapas previstas (ordem do backlog): PA-1..PA-4 (análises sobre a matriz) + análise PA-5 (interestadual) → índice de dependência → painel Streamlit.*
