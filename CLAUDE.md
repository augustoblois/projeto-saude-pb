# Projeto Saúde — Mapa de Evasão Assistencial da PB

Projeto semestral de Análise de Dados (UFPB, 2026.1) — Augusto + Pedro. **Apresentação: 07/08/2026, escopo ~60h.**

**O produto:** matriz origem→destino de internações da PB (SIH/DATASUS) + índice de dependência por região de saúde, em Streamlit. Decisor: Secretaria Estadual de Saúde PB (regionalização/PPI). Diferencial: não existe em nenhum painel público.

## Onde está cada coisa (estado NÃO vive aqui)
- **Estado atual + decisões + riscos** → wiki `~/wiki/vault/academic/projeto-saude-evasao.md` (entidade `academic-projeto-saude`)
- **Pesquisa de fontes + 7 ideias ranqueadas** → `../saude-pesquisa/brief-fontes-e-ideias.md`
- **Requisitos da disciplina** (etapas P1–P3, arquitetura de pastas, stack) → `../../instrucoes-projeto-semestre/*.png`
- **Fluxo de acesso ao SIH validado** → `smoke_test.py` (FTP direto; a API de conveniência do PySUS não serve — ver wiki)

## Dinâmica de colaboração (Augusto + Pedro via GitHub)
- **`STATUS.md` = referência do Pedro** (quase zero git; usa GitHub Desktop, só `main`, sem branch/PR). **`TASKS.md` = referência dos agentes/Augusto** (nasce com o Project Conduction — não confundir os dois).
- **Território:** Augusto → `src/` + `notebooks/01-*`; Pedro → `notebooks/90-*` + `reports/`. Ninguém edita arquivo do outro.
- **Fim de TODA sessão de trabalho:** atualizar `STATUS.md` (incluindo seção "Pra você, Pedro") + commit + push. Sessão sem push = sessão que não existiu. Cobrar o Augusto disso ao encerrar.
- Parquets congelados são versionados (Pedro clona e já tem os dados); `.dbc`/`.dbf` ficam fora do git.

## Regras fixas do projeto
1. **Dados congelados em parquet local** (`data/raw/`) — nada na apresentação depende de fonte viva.
2. **Ângulo anti-genérico** — se já existe em painel público, está fora.
3. **Sustentabilidade do vínculo** — nada que dependa de linkage individual sensível (lição do ENEM).
4. Stack: Python/pandas/Jupyter + Streamlit; arquitetura de pastas da disciplina (`data/{raw,processed}`, `notebooks/`, `src/`, `outputs/`, `reports/`).
