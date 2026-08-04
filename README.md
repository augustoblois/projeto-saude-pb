# Mapa de Evasão Assistencial da Paraíba

Projeto semestral da disciplina de Análise de Dados (UFPB, 2026.1).

**Painel publicado:** https://projeto-saude-pb.streamlit.app
**Relatório final:** [`reports/relatorio-final.md`](reports/relatorio-final.md)

Analisamos as internações hospitalares do SUS na Paraíba (SIH/DATASUS, ano de 2025) para responder: **quando alguém precisa internar, ele consegue atendimento na sua própria região de saúde — ou é obrigado a viajar?** O resultado é uma matriz origem→destino das internações e um índice de dependência por região de saúde, apresentados em um painel interativo (Streamlit) voltado à Secretaria Estadual de Saúde da PB.

O achado central: quase metade das internações do estado (50,5% no ano) acontece fora do município de residência do paciente, e esse fluxo — quem sai, de onde, para onde — não aparece em nenhum painel público hoje.

## Dados

- **Fonte:** Sistema de Informações Hospitalares (SIH/SUS), via FTP do DATASUS — arquivos `RDPB` de janeiro a dezembro de 2025.
- **Congelados no repositório:** os dados já processados estão versionados em `data/raw/sih_pb_2025_*.parquet`, junto com a base territorial do DATASUS (`data/raw/base_territorial_out25.zip`, que diz a que região de saúde cada município pertence). Clonar o repositório já traz tudo — nada aqui depende de fonte viva no dia da apresentação.
- Os arquivos brutos intermediários (`.dbc`/`.dbf`, formato original do DATASUS) ficam fora do git: pesados e sem utilidade fora do pipeline de conversão.

## Como rodar

Requer **Python 3.11+** (testado em 3.13.3, Windows). Os comandos abaixo são PowerShell.

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

`.venv` é uma cópia isolada do Python só para este projeto — evita que as versões instaladas aqui colidam com as de outro projeto na mesma máquina. As versões estão fixadas (`==`) nas que foram efetivamente testadas, para que o ambiente instalado hoje seja o mesmo daqui a alguns meses.

As dependências estão em dois arquivos, porque são dois usos diferentes:

| Arquivo | Para quê | Pacotes |
|---|---|---|
| `requirements.txt` | rodar o painel — é o que basta para ver o projeto funcionando, e é o que o servidor do painel publicado instala | `streamlit`, `plotly` (gráficos e mapa), `pandas`/`numpy` (agregação), `pyarrow` (leitura dos `.parquet`) |
| `requirements-dev.txt` | reproduzir a análise — abrir os notebooks ou recongelar os dados | `jupyter`, `matplotlib` (figuras de `outputs/figures/`), `pysus`/`pyreaddbc` (leitura dos `.dbc` originais do DATASUS) |

Para o segundo caso, instale os dois (o `-dev` já puxa o outro):

```powershell
pip install -r requirements-dev.txt
```

**3. Abrir o painel**

```powershell
streamlit run app.py
```

O painel sobe em `http://localhost:8501` e abre sozinho no navegador. Nenhum download é feito nesse passo: os dados já vêm congelados no repositório (`data/raw/` e `data/processed/`), então o painel funciona inclusive com a máquina desconectada da internet.

O que aparece: as abas **matriz origem→destino** (para onde vão as internações, com filtros por município/região de origem e por mês), **mapa** (fluxos e polos de atração no território da PB), **índice de dependência** (o quanto cada região de saúde depende de outras para internar seus moradores), **achados & recomendações** (a leitura executiva dos números) e **sobre os dados** (procedência, congelamento e nota metodológica).

### Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `python : o termo não é reconhecido` | Python não está no PATH | Reinstalar Python marcando "Add python.exe to PATH"; reabrir o terminal |
| `não é possível carregar o arquivo ...Activate.ps1` (`execution policy`) | Trava padrão do PowerShell contra scripts | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e repetir o comando |
| `streamlit : o termo não é reconhecido` | Ambiente virtual não está ativo | Confirmar `(.venv)` no início da linha do terminal; se não aparecer, rodar `.venv\Scripts\Activate.ps1` |
| `Port 8501 is already in use` | Já existe um painel aberto em outro terminal | Usar a janela já aberta, ou fechá-la e rodar de novo |
| Painel abre mas os números parecem errados | Cópia local desatualizada | `git pull` e rodar de novo |

### Reproduzir os dados processados (opcional)

`data/processed/` já vem pronto no repositório — o painel não depende deste passo. Para regerar tudo do zero, instale também o `requirements-dev.txt` (acima) e execute os notebooks de `notebooks/` nesta ordem, com o ambiente virtual ativado:

1. `01-tratamento-base.ipynb` — junta os 12 meses de 2025 e acrescenta os nomes dos municípios
2. `01-regiao-saude.ipynb` — atribui a região de saúde de residência e de internação
3. `01-matriz-od.ipynb` — monta a matriz origem→destino e as taxas de evasão
4. `01-indice-dependencia.ipynb` — calcula o índice de dependência por região
5. `01-pa1-concentracao.ipynb`, `01-pa3-porte.ipynb`, `01-pa4-estabilidade.ipynb`, `01-pa5-interestadual.ipynb`, `01-pa6-perfil-demanda.ipynb` — análises que geram as figuras de `outputs/` (o `01-pa6` depende da saída do `01-indice-dependencia`; os demais podem rodar em qualquer ordem depois do passo 3)

Todos os passos rodam offline: a base territorial usada no passo 2 também vem congelada no repositório (`data/raw/base_territorial_out25.zip`), então nenhum notebook busca nada no DATASUS.

Para conferir, direto da base congelada, os números citados na narrativa executiva (`reports/`):

```powershell
python src/conferir_narrativa.py
```

Para re-baixar/completar os dados brutos congelados (opcional — os parquets já estão no repo):

```powershell
python src/congelar_sih.py
```

O script é idempotente: meses que já têm parquet são pulados. Para incorporar um mês novo publicado pelo DATASUS, veja [`docs/dados/atualizacao-mensal.md`](docs/dados/atualizacao-mensal.md).

## Estrutura do repositório

```
data/
  raw/         # parquets congelados do SIH-PB 2025 (versionados)
  processed/   # dados tratados e agregados para análise
notebooks/     # análises exploratórias (Jupyter) — 01-* é a cadeia oficial
src/           # scripts Python (coleta, congelamento e conferência)
docs/
  dados/       # dicionário de dados, definição do índice, atualização mensal
  governanca/  # briefing, PRD e backlog do projeto
  diario-do-projeto.md  # linha do tempo de como o projeto foi construído
outputs/       # figuras, tabelas e geojson gerados pelas análises
reports/       # narrativa executiva e sumário de evidências (apresentação)
app.py         # o painel (Streamlit)
```

## Equipe

- Augusto Blois — dados e código (`src/`, `notebooks/01-*`)
- Pedro Luna — análises e relatórios (`notebooks/90-*`, `reports/`)
