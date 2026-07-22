# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (22/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito** (detalhes na seção abaixo) — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação.
- **Prazo:** apresentação dia 07/08/2026 (16 dias).

## O que aconteceu na última sessão (22/07/2026)

- **Baixamos e guardamos o ano de 2025 completo.** O script `src/congelar_sih.py` baixa os dados do governo e salva tudo dentro do projeto — assim a apresentação nunca depende do site do governo estar no ar. Rodou pra os 12 meses e conferimos que veio tudo certo. **Quando você der Pull, os dados já vêm junto — não precisa baixar nada.**
- **Planejamos o projeto de ponta a ponta**, usando um método de organização de projetos que o Augusto usa. Isso gerou alguns documentos novos na pasta `docs/` — você não precisa ler nenhum deles pra trabalhar (sua referência continua sendo este arquivo aqui), mas pra você saber o que é cada um:
  - `docs/briefing.md` — o resumo da intenção do projeto (o problema, pra quem é, o que não pode faltar).
  - `docs/prd.md` — o plano detalhado: as 5 perguntas que a análise vai responder, de onde vem cada dado, como será o painel e o cronograma até o dia 07/08.
  - `docs/backlog.md` — a lista de tarefas do Augusto, quebrada em pedaços pequenos com critério de "pronto". (O seu guia é sempre o `STATUS.md`.)
- **Três decisões importantes ficaram fechadas:**
  1. O painel será feito em **Streamlit** (ferramenta de Python que transforma análise em site interativo) — consideramos algo mais sofisticado visualmente, mas o professor avalia a análise e a aplicação real, não o visual.
  2. Vamos incluir também os **paraibanos que internaram em outros estados** (Pernambuco, Rio Grande do Norte e Ceará) — descobrimos que esses pacientes ficam nos arquivos dos outros estados, então o script vai baixar e filtrar isso também.
  3. O **índice de dependência** — o número principal do projeto — foi definido: pra cada região de saúde, é a porcentagem dos moradores que precisou internar FORA da própria região. Simples de calcular e de explicar pra qualquer pessoa.

## Pra você, Pedro

1. **Preparar o projeto (uma vez só):** abrir o terminal na pasta do projeto e rodar: `pip install -r requirements.txt` — isso instala tudo que o projeto usa.
2. **Abrir os dados — agora com o ano inteiro:** rodar `jupyter notebook` no terminal (abre no navegador uma ferramenta pra mexer nos dados). Num notebook novo, carregar todos os meses de uma vez:
   ```python
   import pandas as pd
   import glob
   df = pd.concat(pd.read_parquet(f) for f in sorted(glob.glob("data/raw/sih_pb_2025_*.parquet")))
   ```
   Cada linha é uma internação. As duas colunas mais importantes: `MUNIC_RES` (código da cidade onde o paciente **mora**) e `MUNIC_MOV` (código da cidade onde ele **internou**). Quando as duas são diferentes, o paciente viajou pra internar — é isso que o projeto investiga.
3. **Explorar e anotar:** salvar seu notebook na pasta `notebooks/` com nome começando em `90-` (ex: `90-eda-pedro.ipynb`). Perguntas boas pra começar: o movimento de internações muda ao longo do ano? Quais cidades mais "mandam" pacientes pra fora? Pra onde eles vão?
4. **Terminou?** GitHub Desktop → **Commit** (dar um nome pro que você fez) → **Push** (enviar pro GitHub, pro Augusto ver).

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
