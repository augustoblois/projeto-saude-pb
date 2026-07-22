# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → **Pull** → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. Atualizado a cada sessão de trabalho do Augusto.

## Onde estamos (22/07/2026)

- **Tema fechado:** matriz origem→destino de internações da PB (SIH/DATASUS) + índice de dependência por região de saúde, entregue em Streamlit. Decisor: Secretaria Estadual de Saúde (regionalização/PPI).
- **Viabilidade confirmada hoje:** baixamos janeiro/2025 do DATASUS ponta-a-ponta. 20.029 internações, 0 nulos nas colunas-chave, e **47,8% dos pacientes internam fora do município onde moram** — a tese do projeto já aparece em 1 mês de dado cru.
- **Prazo:** apresentação 07/08/2026 (16 dias).

## Última sessão (22/07/2026)

- Smoke test do acesso ao SIH passou (`smoke_test.py`).
- Repo criado no GitHub com estrutura da disciplina.
- Dado de jan/2025 congelado em `data/raw/sih_pb_2025_01.parquet` — **já vem no clone, você não precisa baixar nada do DATASUS**.

## Pra você, Pedro

1. **Setup (uma vez só):** instalar Python 3.11+, depois no terminal dentro da pasta do projeto: `pip install -r requirements.txt`.
2. **Explorar o dado:** abrir Jupyter, carregar `data/raw/sih_pb_2025_01.parquet` com `pd.read_parquet(...)`. Colunas-chave: `MUNIC_RES` (onde o paciente mora) e `MUNIC_MOV` (onde internou).
3. **Anotar achados** num notebook seu em `notebooks/` (prefixo `90-`, ex: `90-eda-pedro.ipynb`): quais especialidades/procedimentos mais aparecem? Quais municípios mais "exportam" pacientes?
4. Terminou? GitHub Desktop → **Commit** → **Push**.

## Regras de convivência no repo

- **Território:** Augusto mexe em `src/` e `notebooks/01-*`; Pedro em `notebooks/90-*` e `reports/`. Ninguém edita arquivo do outro — assim nunca dá conflito.
- **Ritual:** Pull antes de começar, Commit + Push quando terminar. Sempre.
- Dúvida rápida → WhatsApp. Decisão importante → registrada aqui.
