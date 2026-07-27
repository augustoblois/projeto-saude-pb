# Sumário de evidências — Mapa de Evasão Assistencial da PB

> **Para que serve este arquivo.** Toda afirmação da narrativa executiva
> (`reports/narrativa-executiva.md`) e toda recomendação apoiada nela citam um número.
> Aqui está a lista completa desses números, cada um com o arquivo de onde ele sai.
> A regra do projeto (RNF-05) é que nenhum número apareça digitado à mão: se está no
> texto, está nesta tabela, e daqui se chega ao notebook que o calculou.
>
> Base de todos os números: SIH/DATASUS, competências jan–dez/2025, congeladas em
> `data/raw/` e tratadas em `data/processed/sih_pb_2025_regioes.parquet`.

## Como ler a coluna "onde conferir"

O nome de um notebook (`01-*.ipynb`) significa: abrir, rodar do começo ao fim, e o
número aparece na seção indicada. O nome de um arquivo `.csv`/`.parquet` significa: o
número está na tabela, sem precisar rodar nada.

---

## 1. Números do estado (o tamanho do problema)

| # | Número | Valor | Onde conferir |
|---|---|---|---|
| E-01 | Internações realizadas em hospitais da PB em 2025 | 258.125 | `01-tratamento-base.ipynb` §3 · `src/conferir_narrativa.py` |
| E-02 | Dessas, de pessoas que moram na PB | 256.623 | `01-regiao-saude.ipynb` §6 · `src/conferir_narrativa.py` |
| E-03 | Internações fora do município onde o paciente mora | 130.379 (50,5%) | `01-matriz-od.ipynb` §7 · `src/conferir_narrativa.py` |
| E-04 | O mesmo, contando só quem mora na PB | 128.877 (50,2%) | `src/conferir_narrativa.py` |
| E-05 | Internações fora da **região de saúde** de residência | 67.633 (26,4%) | `01-indice-dependencia.ipynb` §6 · `src/conferir_narrativa.py` |
| E-06 | Municípios da PB com qualquer internação SUS registrada no ano | 62 de 223 | `01-pa1-concentracao.ipynb` §8 |

> **Cuidado ao citar E-03 vs. E-04.** São medidas diferentes, ambas corretas: E-03 conta
> todas as internações feitas na Paraíba (inclusive de gente de outros estados que veio
> se internar aqui); E-04 conta só residentes da PB. Na narrativa usamos **E-04** quando
> a frase fala de "paraibanos", e E-03 quando fala do movimento hospitalar do estado.

> **Sobre o 47,8%.** O número que motivou o projeto na fase de pesquisa era 47,8% para
> janeiro/2025. Ao refazer a conta com a base congelada — por cinco caminhos
> independentes — o resultado é 49,8%, sempre. Adotamos o número que conseguimos provar.
> A investigação está registrada em `01-matriz-od.ipynb`.

## 2. PA-1 — para onde vai quem sai da própria cidade

| # | Número | Valor | Onde conferir |
|---|---|---|---|
| P1-01 | João Pessoa recebe | 43.624 (33,5%) | `01-pa1-concentracao.ipynb` §8 |
| P1-02 | Campina Grande recebe | 32.817 (25,2%) | `01-pa1-concentracao.ipynb` §8 |
| P1-03 | **Os dois polos juntos** | **58,6%** | `outputs/tables/pa1_ranking_destinos.csv` |
| P1-04 | Com Patos (três polos) | 67,2% | `outputs/tables/pa1_ranking_destinos.csv` |
| P1-05 | Municípios necessários para explicar 80% do fluxo | 7 | `01-pa1-concentracao.ipynb` §3 |
| P1-06 | Municípios necessários para explicar 90% do fluxo | 11 | `01-pa1-concentracao.ipynb` §3 |
| P1-07 | Municípios que recebem algum paciente de fora | 55 | `01-pa1-concentracao.ipynb` §2 |
| P1-08 | Estabilidade mensal dos dois polos | entre 56,6% e 61,3% | `01-pa1-concentracao.ipynb` §5 |
| P1-09 | Sensibilidade: só residentes PB, dois polos | 58,5% | `01-pa1-concentracao.ipynb` §4 |

**Veredito PA-1: CONFIRMADA.** A rede não funciona como malha de municípios que se
apoiam; funciona como funil para dois endereços. Sobreviveu às duas checagens que
poderiam derrubá-la (P1-08 e P1-09).

## 3. PA-2 — índice de dependência por região de saúde

Fonte da tabela completa: `data/processed/indice_dependencia_regional.csv`
(calculada em `01-indice-dependencia.ipynb`).

| # | Número | Valor | Onde conferir |
|---|---|---|---|
| P2-01 | **Regiões com dependência alta (índice > 50%)** | **8 de 16** | `indice_dependencia_regional.csv` |
| P2-02 | Região mais dependente: 3ª Região | 84,5% | `indice_dependencia_regional.csv` |
| P2-03 | Menos dependentes: 1ª Mata Atlântica (João Pessoa) e 16ª (Campina Grande) | 1,8% e 4,1% | `indice_dependencia_regional.csv` |
| P2-04 | Taxa do estado inteiro (67.633 de 256.623) | 26,4% | `01-indice-dependencia.ipynb` §6 · `src/conferir_narrativa.py` |

> **Rótulo com cuidado.** O 26,4% é a taxa **agregada do estado** (todas as internações
> de residentes que saíram da região, sobre o total). Não é a média aritmética dos 16
> índices — essa daria outro valor, porque região grande e região pequena pesariam igual.
> No painel e na narrativa ele aparece como "taxa estadual", nunca como "média".

### 3.1 Para onde vai cada uma das 8 regiões críticas

Calculado a partir de `data/processed/matriz_od_regional_mensal.csv` (US-04).

| Região de origem | Destino principal | Volume | % de todas as saídas dela |
|---|---|---|---|
| 3ª Região | 16ª (Campina Grande) | 7.639 de 9.143 | 83,6% |
| 14ª Região | 1ª Mata Atlântica (João Pessoa) | 4.847 de 5.249 | 92,3% |
| 15ª Região | 16ª (Campina Grande) | 6.115 de 6.826 | 89,6% |
| 2ª Região | 1ª Mata Atlântica (João Pessoa) | 7.593 de 8.986 | 84,5% |
| 4ª Região | 16ª (Campina Grande) | 3.145 de 3.837 | 82,0% |
| 12ª Região | 1ª Mata Atlântica (João Pessoa) | 5.158 de 7.479 | 69,0% |
| 11ª Região | 6ª (Patos) | 1.357 de 2.329 | 58,3% |
| 7ª Região | 6ª (Patos) | 1.814 de 5.029 | 36,1% |

**Leitura:** em **7 das 8** regiões críticas, a maioria das saídas vai para um único
destino. A dependência não é difusa (um pouco para cada vizinho) — é dependência de um
endereço só. A 7ª Região é a única exceção: a saída dela é realmente espalhada.

*Recalculável com* `python src/conferir_narrativa.py`.

**Veredito PA-2: CONFIRMADA** (hipótese era "≥ 1/3 das regiões com índice > 50%";
resultado: 8/16 = 50%). O índice foi validado por quatro caminhos de cálculo
independentes, com divergência < 0,05 ponto percentual.

## 4. PA-3 — evasão × porte do município

Fonte: `outputs/tables/pa3_evasao_por_porte.csv` e `pa3_saldo_municipios.csv`
(calculadas em `01-pa3-porte.ipynb`).

| Porte do município | Municípios | Taxa de evasão |
|---|---|---|
| Até 10 mil habitantes | 140 | **98,1%** |
| 10 a 20 mil | 50 | 80,4% |
| 20 a 50 mil | 22 | 64,9% |
| 50 a 100 mil | 7 | 53,0% |
| Acima de 100 mil | 4 | **9,3%** |

| # | Número | Valor | Onde conferir |
|---|---|---|---|
| P3-01 | Cidades de até 10 mil hab. que **não internaram nenhum** morador no ano | 133 de 140 (95%) | `01-pa3-porte.ipynb` §5 |
| P3-02 | Saldo de João Pessoa (recebe menos manda) | +41.761 | `pa3_saldo_municipios.csv` · §6 |
| P3-03 | Saldo de Campina Grande | +32.233 | `pa3_saldo_municipios.csv` · §6 |
| P3-04 | João Pessoa: taxa de evasão dos próprios moradores | 3,6% | `01-pa3-porte.ipynb` §3 |
| P3-05 | Campina Grande: idem | 1,8% | `01-pa3-porte.ipynb` §3 |

**Veredito PA-3: CONFIRMADA**, e a relação é monotônica — a taxa cai a cada faixa de
porte, sem uma única inversão.

## 5. PA-4 — estabilidade do fluxo ao longo do ano

Fonte: `outputs/tables/pa4_top_pares_od.csv` e `pa4_permanencia_mensal.csv`
(calculadas em `01-pa4-estabilidade.ipynb`).

| # | Número | Valor | Onde conferir |
|---|---|---|---|
| P4-01 | Dos 20 maiores fluxos do ano, quantos estão no top 20 de **todos** os 12 meses | 13 | `pa4_permanencia_mensal.csv` |
| P4-02 | Sobreposição média mês×ano | 17,1 de 20 (85%) | `01-pa4-estabilidade.ipynb` §4 (restatado no §10) |
| P4-03 | Pior mês (dezembro) | 14 de 20 | `pa4_permanencia_mensal.csv` |
| P4-04 | Correlação de ranking mês×ano | sempre > 0,90 | `01-pa4-estabilidade.ipynb` §4 (restatado no §10) |

**Veredito PA-4: CONFIRMADA — o fluxo é estrutural.** As trocas de posição acontecem na
borda do ranking, entre pares de tamanho quase idêntico, não no topo.

> **Ressalva sobre dezembro.** É a competência mais sujeita a retificação posterior pelo
> DATASUS. Dezembro tem o menor volume do ano *e* a menor sobreposição — com esta base
> não dá para separar queda real de registro ainda não consolidado. Fica declarado, sem
> extrapolação.

## 6. PA-5 — fluxo interestadual

Fonte: `outputs/tables/pa5_ranking_destinos.csv` e
`pa5_perfil_fronteira_complexidade.csv` (calculadas em `01-pa5-interestadual.ipynb`).

| # | Número | Valor | Onde conferir |
|---|---|---|---|
| P5-01 | Paraibanos internados em PE, RN ou CE em 2025 | 3.682 | `pa5_ranking_destinos.csv` |
| P5-02 | Sobre todas as internações de residentes da PB | 1,4% | `01-pa5-interestadual.ipynb` §2 |
| P5-03 | Fatia do fluxo interestadual que vai para Recife | 41% | `pa5_ranking_destinos.csv` · §3 |
| P5-04 | Complexidade do grupo "interior" vs. "fronteira" | 1,7× a 2,8× maior | `pa5_perfil_fronteira_complexidade.csv` · §6 |
| P5-05 | Segundo maior destino interestadual | Alexandria/RN | `pa5_ranking_destinos.csv` |

**Veredito PA-5: fenômeno MISTO.** Fronteira e alta complexidade convivem.

> **O que NÃO pode ser citado como número firme.** A divisão do volume entre "casos de
> fronteira" e "casos de interior" depende do corte de distância adotado e varia de 11,5%
> a 58,5% — chega a inverter qual grupo é maioria. Esse número **não entra na narrativa**.
> O que é robusto, e se mantém em todos os cortes testados, é a diferença de perfil
> clínico (P5-04): quem sai do interior sempre tem complexidade maior que quem sai da
> fronteira.

---

## 7. Rastreamento: cada recomendação e sua âncora

| Recomendação (ver `narrativa-executiva.md`) | Evidências que a sustentam |
|---|---|
| R1 — Financiar formalmente os polos na PPI | P1-03, P3-02, P3-03 |
| R2 — Priorizar as 8 regiões de dependência alta | P2-01, P2-02, tabela 3.1 |
| R3 — Usar a matriz origem→destino como base de cálculo | P4-01, P4-02, P4-04 |
| R4 — Pactuação interestadual + oncologia no interior | P5-01, P5-03, P5-04, P5-05 |
| Fecho — A unidade de planejamento é a região | P3-01, faixas da PA-3, E-06 |

## 8. Limitações que valem para tudo acima

Estas cinco atravessam todas as análises e devem ser ditas em voz alta na apresentação,
antes que alguém pergunte:

1. **Cada linha é uma internação, não uma pessoa.** Quem internou três vezes conta três
   vezes. Os números medem volume de deslocamento, não quantidade de indivíduos.
2. **Só internações pelo SUS.** A rede privada não está no SIH. Em municípios com mais
   leitos privados, o retrato subestima a oferta local total.
3. **Todos os índices são um piso, não o valor real.** Paraibano internado em outro
   estado não aparece na base principal — a dependência real é igual ou maior que a
   medida, nunca menor. A PA-5 dimensiona esse pedaço em 1,4%.
4. **Trocar de município não é o mesmo que percorrer distância.** Bayeux e Santa Rita
   "evadem" muito porque são coladas em João Pessoa: o morador atravessa uma avenida.
5. **Um ano só (2025).** "Estável ao longo de 2025" não é "estável ao longo dos anos".

As limitações específicas de cada análise estão escritas por extenso no veredito do
notebook correspondente, e as do índice em `docs/definicao-indice-dependencia.md` §6.
