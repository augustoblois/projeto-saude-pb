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

---

*Próximas etapas previstas (ordem do backlog): US-02 (região de saúde por internação) → US-04 (matriz origem→destino) → análises PA-1..PA-5 → índice de dependência → painel Streamlit.*
