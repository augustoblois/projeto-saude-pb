# Mapa de Evasão Assistencial da Paraíba

Projeto semestral da disciplina de Análise de Dados (UFPB, 2026.1).

Analisamos as internações hospitalares do SUS na Paraíba (SIH/DATASUS, ano de 2025) para responder: **quando alguém precisa internar, ele consegue atendimento na sua própria região de saúde — ou é obrigado a viajar?** O resultado é uma matriz origem→destino das internações e um índice de dependência por região de saúde, apresentados em um painel interativo (Streamlit) voltado à Secretaria Estadual de Saúde da PB.

## Dados

- **Fonte:** Sistema de Informações Hospitalares (SIH/SUS), via FTP do DATASUS — arquivos `RDPB` de janeiro a dezembro de 2025.
- **Congelados no repositório:** os dados já processados estão versionados em `data/raw/sih_pb_2025_*.parquet`, junto com a base territorial do DATASUS (`data/raw/base_territorial_out25.zip`, que diz a que região de saúde cada município pertence). Quem clona o repo já tem tudo — nada aqui depende de fonte viva.
- Os arquivos brutos intermediários (`.dbc`/`.dbf`) ficam fora do git.

## Como rodar

Requer Python 3.11+ (testado em 3.13.3, Windows). Os comandos abaixo são PowerShell.

> Nunca rodou um projeto Python antes? Use o [`COMECE-AQUI.md`](COMECE-AQUI.md) — mesmo caminho, explicado passo a passo, com o que fazer em cada erro.

**1. Clonar o repositório e entrar na pasta**

```powershell
git clone <url-do-repo> projeto-saude
cd projeto-saude
```

**2. Criar o ambiente virtual e instalar as dependências**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

As versões em `requirements.txt` estão fixadas (`==`) nas que foram efetivamente testadas, para que o ambiente instalado hoje seja o mesmo daqui a alguns meses.

**3. Abrir o painel**

```powershell
streamlit run app.py
```

O painel sobe em `http://localhost:8501` e abre sozinho no navegador. Nenhum download é feito nesse passo: os dados já vêm congelados no repositório (`data/raw/` e `data/processed/`), então o painel funciona inclusive com a máquina desconectada da internet.

O que aparece: as abas **matriz origem→destino** (para onde vão as internações, com filtros por município/região de origem e por mês), **mapa** (fluxos e polos de atração no território da PB), **índice de dependência** (o quanto cada região de saúde depende de outras para internar seus moradores), **achados & recomendações** (a leitura executiva dos números) e **sobre os dados** (procedência, congelamento e nota metodológica).

### Reproduzir os dados processados (opcional)

`data/processed/` já vem pronto no repositório — o painel não depende deste passo. Para regerar tudo do zero, execute os notebooks de `notebooks/` nesta ordem, com o ambiente virtual ativado (`.venv\Scripts\Activate.ps1`) antes de abrir o Jupyter:

1. `01-tratamento-base.ipynb` — junta os 12 meses de 2025 e acrescenta os nomes dos municípios
2. `01-regiao-saude.ipynb` — atribui a região de saúde de residência e de internação
3. `01-matriz-od.ipynb` — monta a matriz origem→destino e as taxas de evasão
4. `01-indice-dependencia.ipynb` — calcula o índice de dependência por região
5. `01-pa1-concentracao.ipynb`, `01-pa3-porte.ipynb`, `01-pa4-estabilidade.ipynb`, `01-pa5-interestadual.ipynb`, `01-pa6-perfil-demanda.ipynb` — análises que geram as figuras de `outputs/` (podem rodar em qualquer ordem depois do passo 3)

Todos os passos rodam offline: a base territorial usada no passo 2 também vem congelada no repositório (`data/raw/base_territorial_out25.zip`), então nenhum notebook busca nada no DATASUS.

Para re-baixar/completar os dados brutos congelados (opcional — os parquets já estão no repo):

```powershell
python src/congelar_sih.py
```

O script é idempotente: meses que já têm parquet são pulados.

Para incorporar um mês novo publicado pelo DATASUS, veja [`docs/atualizacao-mensal.md`](docs/atualizacao-mensal.md).

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
app.py         # o painel (Streamlit)
STATUS.md      # estado atual do projeto em linguagem simples
```

## Equipe

- Augusto Blois — dados e código (`src/`, `notebooks/01-*`)
- Pedro Luna — análises e relatórios (`notebooks/90-*`, `reports/`)

O andamento do projeto está sempre resumido no [`STATUS.md`](STATUS.md).
