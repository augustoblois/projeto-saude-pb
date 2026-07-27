# Como entra um mês novo de dados

Este documento responde a uma pergunta só: **o DATASUS publicou mais um mês — o que eu
rodo, em que ordem, e o que espero que aconteça com os números?**

O projeto foi construído para ser *reprodutível sem internet no dia da apresentação*: tudo
o que o painel mostra sai de arquivos congelados dentro do repositório. Atualizar é,
portanto, um ato deliberado — ninguém "puxa" dado novo por acidente.

---

## 1. O ciclo, em uma frase

> O DATASUS publica o lote de um mês com cerca de **dois meses de atraso** →
> `python src/congelar_sih.py` baixa e congela esse mês em `data/raw/` →
> os notebooks `01-*` são reexecutados na ordem da seção 3 →
> o painel (`streamlit run app.py`) passa a exibir o mês novo sem nenhuma mudança de código.

---

## 2. O comando exato

Do **diretório raiz do projeto** (os caminhos dentro dos scripts são relativos a ele; rodar
de dentro de `src/` não funciona), com o ambiente virtual ativo:

```powershell
python src/congelar_sih.py
```

### O que esse comando faz, passo a passo

1. Abre **uma** conexão FTP com `ftp.datasus.gov.br` e lista os arquivos do SIH/SUS.
2. Para cada mês do período configurado, procura o arquivo `RDPB{AA}{MM}.dbc`
   (`RD` = AIH reduzida, `PB` = arquivos de hospitais da Paraíba).
3. Baixa o `.dbc`, converte para `.dbf` e daí para DataFrame.
4. **Valida antes de gravar**: as colunas `MUNIC_RES` (onde o paciente mora) e `MUNIC_MOV`
   (onde ele foi internado) precisam existir e não ter nenhum nulo. Se falharem, o mês é
   reportado como erro e **nenhum parquet é escrito** para ele.
5. Grava `data/raw/sih_pb_{ANO}_{MM}.parquet` e imprime um placar final mês a mês.

### Idempotência — rodar de novo é seguro

O script monta a lista de faltantes assim: `[m for m in MESES if not (OUT / f"sih_pb_{ANO}_{m:02d}.parquet").exists()]`.

Ou seja: **mês que já tem parquet é pulado, sem download e sem reescrita.** Rodar o comando
dez vezes seguidas só completa o que falta. Se a conexão cair no meio, é só rodar de novo —
os meses já congelados não são refeitos. Uma falha em um mês não derruba os outros (cada
conversão está em `try/except` própria).

O placar final distingue três estados por mês: `OK — N internações`, `já congelado`, e
`AUSENTE no FTP` (o DATASUS ainda não publicou aquele lote).

### Como apontar para outro ano / outros meses

O período **não** é passado por linha de comando. São duas constantes no topo de
`src/congelar_sih.py`:

```python
ANO = 2025
MESES = range(1, 13)
```

Para congelar jan–mar/2026, por exemplo: `ANO = 2026` e `MESES = range(1, 4)`.

⚠️ **Atenção — mudar `ANO` não é só uma constante.** O nome do ano está no nome dos
arquivos e o restante do pipeline procura por `2025` literalmente:

| Onde | O que está fixado em 2025 |
|---|---|
| `src/congelar_sih.py` | `ANO = 2025` → nomes `sih_pb_2025_MM.parquet` |
| `src/congelar_sih_vizinhos.py` | `ANO = 2025` → `sih_pb_residentes_fora_2025.parquet` |
| `notebooks/01-tratamento-base.ipynb` | `DATA_RAW.glob("sih_pb_2025_*.parquet")` e a saída `sih_pb_2025_tratado.parquet` |
| `notebooks/01-regiao-saude.ipynb` | lê/escreve os arquivos `..._2025_...` |

Acrescentar **meses do mesmo ano** (o caso normal do ciclo mensal) não exige tocar em nada
disso: basta ampliar `MESES` e o `glob` já captura o arquivo novo. Trocar **de ano** exige
uma passada nos quatro pontos acima — é trabalho de meia hora, não de refatoração, mas
precisa ser consciente.

### O recorte interestadual (opcional)

A análise PA-5 (paraibanos internados em PE/RN/CE) tem script próprio, porque os arquivos do
SIH são organizados pela UF **do hospital** — um paraibano internado em Recife está no
arquivo de Pernambuco, nunca no da Paraíba:

```powershell
python src/congelar_sih_vizinhos.py
```

Ele também é idempotente (guarda fatias por UF×mês em `data/raw/_staging_vizinhos/`, fora do
git) e tem um guard-rail duro: **só escreve o parquet final quando todas as fatias do período
existem** — recorte parcial não entra na base, para não enviesar a comparação entre UFs.
Se o parquet final já existir, ele apenas revalida, sem baixar nada.

### O que **não** precisa ser baixado de novo

As tabelas auxiliares são estruturais, não mensais. Já estão versionadas no repositório e só
se mexem quando o IBGE/SES-PB mudam algo (mudança de nome de município, nova estimativa
populacional, revisão da malha de regiões):

`src/baixar_municipios_ibge.py` · `src/baixar_populacao_ibge.py` ·
`src/baixar_base_territorial.py` · `src/baixar_malha_pb.py`

---

## 3. A cadeia de reprocessamento

Congelar o parquet **não** muda o painel. O painel lê apenas as pré-agregações de
`data/processed/` e `outputs/` — é preciso regenerá-las. A ordem abaixo foi derivada lendo as
leituras e escritas de cada notebook (`read_parquet`/`read_csv` × `to_parquet`/`to_csv`/`savefig`),
não da numeração dos arquivos.

### Cadeia obrigatória (sequencial — cada passo consome a saída do anterior)

| # | Rodar | Lê | Regenera |
|---|---|---|---|
| 1 | `notebooks/01-tratamento-base.ipynb` | `data/raw/sih_pb_2025_*.parquet`, `data/raw/municipios_ibge.csv` | `data/processed/sih_pb_2025_tratado.parquet` |
| 2 | `notebooks/01-regiao-saude.ipynb` | o parquet tratado do passo 1 | `data/processed/regioes_saude_pb.csv`, `data/processed/sih_pb_2025_regioes.parquet` |
| 3 | `notebooks/01-matriz-od.ipynb` | `sih_pb_2025_regioes.parquet` | `data/processed/matriz_od_municipal_mensal.parquet`, `matriz_od_regional_mensal.csv`, `taxas_evasao_regional.csv` |

Depois do passo 3 a **aba Matriz O-D e a aba Mapa do painel já estão corretas** — as duas
consomem só `matriz_od_municipal_mensal.parquet` / `matriz_od_regional_mensal.csv`.

### Análises que dependem da matriz (podem rodar em qualquer ordem entre si)

| Rodar | Lê | Regenera |
|---|---|---|
| `notebooks/01-pa1-concentracao.ipynb` | `matriz_od_municipal_mensal.parquet` | `outputs/tables/pa1_ranking_destinos.csv`, `outputs/figures/pa1_concentracao_destino.png` |
| `notebooks/01-pa3-porte.ipynb` | matriz municipal + `data/raw/populacao_ibge_municipios.csv`, `municipios_ibge.csv` | `outputs/tables/pa3_evasao_por_porte.csv`, `pa3_saldo_municipios.csv`, `outputs/figures/pa3_evasao_x_porte.png` |
| `notebooks/01-pa4-estabilidade.ipynb` | `matriz_od_municipal_mensal.parquet` | `outputs/tables/pa4_top_pares_od.csv`, `pa4_permanencia_mensal.csv`, `outputs/figures/pa4_estabilidade_fluxo.png` |
| `notebooks/01-pa5-interestadual.ipynb` | `data/raw/sih_pb_residentes_fora_2025.parquet` + `sih_pb_2025_regioes.parquet` | `outputs/tables/pa5_ranking_destinos.csv`, `pa5_perfil_fronteira_complexidade.csv`, `outputs/figures/pa5_destino_concentracao.png`, `pa5_fronteira_complexidade.png` |

> `01-pa5` depende do congelamento dos vizinhos, não da matriz — mas depende do passo 2.

### Índice e perfil (sequenciais, e nesta ordem)

| # | Rodar | Lê | Regenera |
|---|---|---|---|
| 4 | `notebooks/01-indice-dependencia.ipynb` | `regioes_saude_pb.csv`, `matriz_od_regional_mensal.csv`, `matriz_od_municipal_mensal.parquet`, `sih_pb_2025_regioes.parquet`, `taxas_evasao_regional.csv` | `data/processed/indice_dependencia_regional.csv`, `outputs/figures/indice_ranking_dependencia.png` |
| 5 | `notebooks/01-pa6-perfil-demanda.ipynb` | `sih_pb_2025_regioes.parquet` **+ `indice_dependencia_regional.csv`** (saída do passo 4) | `outputs/tables/pa6_assinatura_regiao.csv`, `pa6_classificacao_evasao.csv`, `pa6_recomendacao_regiao.csv`, `pa6_teste_robustez_desfecho.csv`, `outputs/figures/pa6_heatmap_excesso_especialidade.png`, `pa6_tipo_dominante_regioes_prioritarias.png` |

**`01-pa6` depois de `01-indice-dependencia`, sempre** — é a única dependência entre análises
que não passa pela matriz, e inverter a ordem faz o pa6 ler um índice desatualizado sem
reclamar de nada.

### Fechamento

```powershell
python src/conferir_narrativa.py     # recalcula da base os números do texto executivo
streamlit run app.py                 # confere o painel
```

`reports/narrativa-executiva.md` e `reports/sumario-evidencias.md` **não** se atualizam
sozinhos: são texto. Se os números mudarem, o texto precisa ser reescrito à mão — e
`conferir_narrativa.py` existe exatamente para dizer quais números saíram do lugar.
(Território do Pedro: `reports/` é dele.)

---

## 4. Os `assert` vão falhar — e isso é o desenho, não um bug

Os notebooks estão cheios de verificações com números fixos de 2025:

```python
assert TOTAL_FORA == 130379, f"Universo da PA-1 divergiu: {TOTAL_FORA}"
assert int(caminho_A["internacoes_residentes"].sum()) == 256623
assert TOTAL_BASE == 258125, "A matriz O-D nao tem o total esperado de internacoes!"
assert total_jan == 20029, f"Volume de jan/2025 divergiu: {total_jan}"
```

Esses números **travam a base auditada da apresentação**. Enquanto o recorte for jan–dez/2025,
qualquer divergência é sinal de que algo quebrou no caminho — e o notebook para de rodar em vez
de produzir um gráfico silenciosamente errado.

No momento em que um mês novo entrar, eles vão falhar **por construção**: o total mudou de
propósito. O procedimento correto é:

1. Rodar a cadeia e **anotar** cada `assert` que falhou, com o valor antigo e o novo.
2. Conferir se a variação é compatível com o volume do mês acrescentado (a PB roda na faixa de
   ~19 a 23 mil internações/mês). Salto fora dessa faixa = investigar antes de atualizar o número.
3. Só então substituir a constante do `assert` pelo novo valor — nunca apagar o `assert`.

Trocar o número sem conferir a variação transforma uma trava de qualidade em decoração.

---

## 5. Nota metodológica — retificações (e por que dezembro é o caso sensível)

### O fato

O SIH não é um retrato definitivo. O DATASUS **retifica competências já publicadas**: AIH
enviada com atraso, correção de registro pelo hospital e reprocessamento pelo gestor entram no
arquivo de um mês *depois* que aquele mês já foi publicado. Na prática, uma competência recém
publicada chega **incompleta e sobe** ao longo dos meses seguintes, até estabilizar.

Consequência direta e desconfortável: **o mesmo comando, rodado em duas datas diferentes,
pode devolver números diferentes para o mesmo mês.** Isso não é erro do pipeline.

### Por que dezembro

Dezembro é o mês mais exposto porque é o último a ser congelado — é a competência com menos
tempo de maturação quando a base é fechada. No recorte deste projeto, dezembro/2025 tem
simultaneamente o **menor volume do ano** e a **menor sobreposição de pares origem→destino**
(14 dos 20 maiores pares, contra estabilidade quase total nos demais meses). Com esta base
**não é possível separar** "houve menos internação de fato" de "o registro ainda não
consolidou".

### A política do projeto

Esta política **já estava registrada** antes deste documento — aqui ela só é reunida num lugar
só. Fontes no repositório:

- `docs/prd.md` (premissas): *"dezembro pode ainda receber retificações do DATASUS (AIH
  atrasada) — declarado como nota metodológica, sem exclusão de meses"*.
- `docs/definicao-indice-dependencia.md`, §6(f): retificações de dezembro podem mexer
  marginalmente nos números; **nenhum mês foi excluído**.
- `notebooks/01-pa4-estabilidade.ipynb` (limitação 3) e `reports/sumario-evidencias.md`
  ("Ressalva sobre dezembro"): a queda de fim de ano pode ser dado ainda incompleto; fica
  declarado, sem extrapolar.

Em uma frase: **nenhum mês é excluído, nenhuma correção é estimada, e a incerteza é declarada
no texto em vez de ser maquiada.** Excluir dezembro "por precaução" inventaria um ano de onze
meses; projetar a retificação inventaria dado que não existe. Declarar é a única opção honesta
com o que a base sustenta.

### O que isso significa para quem reprocessar

- **Recongelar um mês antigo muda números já publicados.** O script *não* faz isso sozinho —
  a idempotência protege: mês com parquet existente é pulado. Para forçar a atualização de uma
  competência é preciso **apagar o parquet daquele mês à mão** e rodar o script de novo. É uma
  decisão consciente, nunca um efeito colateral.
- **Regra prática:** trate uma competência como estável a partir de **~3 meses** da publicação.
  Abaixo disso, o número ainda está subindo.
- Ao acrescentar o mês mais recente, espere que ele apareça **subdimensionado** frente aos
  meses maduros. Não interprete isso como queda de demanda.
- Se recongelar meses antigos, **rode a cadeia inteira da seção 3** — matriz, índice e PA6 são
  todos derivados; deixar um deles para trás produz um painel internamente inconsistente.

---

## 6. Checklist de uma atualização

- [ ] `python src/congelar_sih.py` (com `MESES`/`ANO` ajustados) → placar sem `AUSENTE`/`ERRO`
- [ ] (se a PA-5 importar) `python src/congelar_sih_vizinhos.py` → 100% das fatias presentes
- [ ] Notebooks 1 → 2 → 3 da cadeia obrigatória, topo a baixo
- [ ] PA1, PA3, PA4, PA5 (ordem livre) → índice → **PA6 por último**
- [ ] `assert`s que falharam: variação conferida contra a faixa mensal e constantes atualizadas
- [ ] `python src/conferir_narrativa.py` → números do texto reconferidos
- [ ] Textos de `reports/` revisados se algum número mudou
- [ ] `streamlit run app.py` → painel abre completo, **com a internet desligada**
- [ ] Commit dos parquets/CSVs novos (`.dbc` e `.dbf` continuam fora do git)
