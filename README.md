# Mapa de Evasão Assistencial da Paraíba

Projeto semestral da disciplina de Análise de Dados (UFPB, 2026.1).

Analisamos as internações hospitalares do SUS na Paraíba (SIH/DATASUS, ano de 2025) para responder: **quando alguém precisa internar, ele consegue atendimento na sua própria região de saúde — ou é obrigado a viajar?** O resultado é uma matriz origem→destino das internações e um índice de dependência por região de saúde, apresentados em um painel interativo (Streamlit) voltado à Secretaria Estadual de Saúde da PB.

## Dados

- **Fonte:** Sistema de Informações Hospitalares (SIH/SUS), via FTP do DATASUS — arquivos `RDPB` de janeiro a dezembro de 2025.
- **Congelados no repositório:** os dados já processados estão versionados em `data/raw/sih_pb_2025_*.parquet`. Quem clona o repo já tem tudo — nada aqui depende de fonte viva.
- Os arquivos brutos intermediários (`.dbc`/`.dbf`) ficam fora do git.

## Como rodar

Requer Python 3.11+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Para re-baixar/completar os dados congelados (opcional — os parquets já estão no repo):

```powershell
python src/congelar_sih.py
```

O script é idempotente: meses que já têm parquet são pulados.

## Estrutura do repositório

```
data/
  raw/         # parquets congelados do SIH-PB 2025 (versionados)
  processed/   # dados tratados para análise
notebooks/     # análises exploratórias (Jupyter)
src/           # scripts Python (coleta e processamento)
docs/          # briefing, PRD e backlog do projeto
outputs/       # figuras e resultados gerados
reports/       # relatórios das etapas da disciplina
STATUS.md      # estado atual do projeto em linguagem simples
```

## Equipe

- Augusto Blois — dados e código (`src/`, `notebooks/01-*`)
- Pedro — análises e relatórios (`notebooks/90-*`, `reports/`)

O andamento do projeto está sempre resumido no [`STATUS.md`](STATUS.md).
