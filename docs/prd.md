# PRD — Mapa de Evasão Assistencial da PB

> Fonte: docs/briefing.md (aprovado). Gerado pelo pm-agent.
> Projeto de ANÁLISE DE DADOS (UFPB, disciplina Análise de Dados) — não é web-app fullstack. Stack: Python/pandas/Jupyter + Streamlit.

## ⚠️ Gaps para o gate
- **Troca de projeto ainda não formalizada com o professor.** Ele sinalizou aceite, mas a conversa não aconteceu. Todo o escopo abaixo assume aprovação — é o único evento capaz de invalidar o PRD inteiro.

## Problema & visão
Quase metade das internações da Paraíba (49,8% em jan/2025; 20.029 internações no mês) acontece fora do município de residência do paciente, e **nenhum painel público mostra esse fluxo origem→destino**. O gestor da SES-PB decide pactuação (PPI) e regionalização sem enxergar a evasão assistencial. Este projeto entrega a peça que falta: uma matriz origem→destino das internações de 2025 (SIH/DATASUS) + um índice de dependência por região de saúde, num painel Streamlit que um gestor real poderia abrir amanhã. No contexto acadêmico, é a entrega P3 (40% da nota, demo ao vivo em 07/08/2026), cujo critério nº 1 é exatamente **viabilidade real**.

## Objetivos (mensuráveis)
- **O1 — Demo ao vivo aprovável na rubrica P3.** · métrica: no dia 07/08/2026, o painel abre com `streamlit run`, 100% offline (nenhuma chamada de rede), e cobre os 5 itens da rubrica (análise consolidada, visualizações, comunicação executiva, recomendações, reprodutibilidade).
- **O2 — Matriz O-D inédita e verificável.** · métrica: matriz origem→destino cobrindo todos os meses congelados de 2025, com totais por par (origem, destino) que batem com a contagem bruta do parquet (validação de soma = 100% das internações classificadas em "no município" / "fora do município").
- **O3 — Índice de dependência por região de saúde.** · métrica: índice calculado para 100% das regiões de saúde da PB, com definição escrita (fórmula + interpretação) que um gestor não-técnico entende em uma leitura.
- **O4 — Recomendações práticas para a SES-PB.** · métrica: ≥ 3 recomendações acionáveis no relatório/painel, cada uma ancorada em um número da análise (nenhuma recomendação sem evidência apontável).
- **O5 — Reprodutibilidade de ponta a ponta.** · métrica: em uma máquina limpa, `git clone` + install de dependências + `streamlit run` reproduz o painel sem baixar nada do DATASUS (parquets versionados no repo).

## Personas
- **Professor da disciplina (avaliador real)** — quem dá a nota da P3 · job: verificar em ~minutos de demo que o produto tem aplicação real, análise consolidada, comunicação executiva e é reprodutível.
- **Gestor da SES-PB (usuário simbólico primário)** — decisor de regionalização/PPI · job: enxergar quais regiões dependem de quais para internação e dimensionar a pactuação com números, não intuição.
- **Jornalista de dados / profissional de saúde (usuários simbólicos secundários)** — comunicadores e ponta assistencial · job: encontrar e citar padrões de evasão que hoje não existem em nenhum painel público.

## Perguntas analíticas & hipóteses iniciais
> Espírito da Entrega 1 do projeto anterior da dupla: pergunta + hipótese falseável. São o roteiro da análise consolidada (O2/O3) e a matéria-prima das recomendações (O4).

- **PA-1 — Concentração de destino.** Para onde vão os pacientes que se internam fora do município de residência? *Hipótese:* João Pessoa e Campina Grande concentram, juntas, mais de 50% das internações de não-residentes — o fluxo é bipolar, não distribuído.
- **PA-2 — Dependência regional.** Quantas regiões de saúde da PB dependem de fora para a maioria das internações dos seus residentes? *Hipótese:* pelo menos um terço das regiões tem índice de dependência > 50% — a "autossuficiência regional" prevista na regionalização não se sustenta nos dados.
- **PA-3 — Evasão e porte do município.** A taxa de evasão cai com o porte do município de residência? *Hipótese:* relação inversa e forte — municípios pequenos exportam quase tudo; os polos (João Pessoa, Campina Grande) têm evasão < 10% e são importadores líquidos.
- **PA-4 — Estabilidade temporal do fluxo.** Os fluxos O-D são estáveis mês a mês em 2025? *Hipótese:* os 20 maiores pares origem→destino se mantêm praticamente os mesmos em todos os meses — a evasão é estrutural (rede assistencial), não circunstancial (surtos, sazonalidade). Se for estrutural, é problema de pactuação, o que sustenta as recomendações à SES-PB.
- **PA-5 — Fluxo interestadual.** Quanto da evasão sai da PB (residentes internados em PE, RN, CE)? *Hipótese:* a evasão interestadual é minoritária (< 15% da evasão total), mas concentrada nas regiões de fronteira — um achado com implicação direta de pactuação interestadual.

## Fontes de dados & variáveis de interesse

**Base principal:** SIH/SUS — Sistema de Informações Hospitalares (DATASUS), grupo **RD (AIH Reduzida)**
**Acesso:** FTP direto do DATASUS, via pipeline próprio de congelamento (`src/congelar_sih.py`) — a API de conveniência do PySUS foi descartada por instabilidade (decisão registrada na wiki do projeto)
**Formato:** `.dbc` (origem) → **parquet** versionado no repositório (`.dbc`/`.dbf` ficam fora do git)
**Janela:** jan–dez/2025 · **UF:** Paraíba (unidade de registro: AIH)
**Escala de referência:** jan/2025 = 20.029 internações, 49,8% fora do município de residência *(corrigido em 23/07/2026: o valor original 47,8% vinha da fase de pesquisa, sem cálculo rastreável; 49,8% é o valor reproduzível — investigação na seção 4 de `notebooks/01-matriz-od.ipynb`)*

**Variáveis de interesse (layout RD):**

| Variável | Descrição | Papel na análise |
|---|---|---|
| `MUNIC_RES` | Município de residência do paciente (código IBGE) | **Origem** da matriz O-D |
| `MUNIC_MOV` | Município do estabelecimento de internação | **Destino** da matriz O-D |
| `ANO_CMPT`, `MES_CMPT` | Ano/mês de competência da AIH | Recorte temporal (PA-4) |
| `DT_INTER` | Data de internação | Recorte temporal fino (apoio) |
| `DIAG_PRINC` | Diagnóstico principal (CID-10) | Caracterização dos fluxos (EP-07) |
| `ESPEC` | Especialidade do leito | Recorte por especialidade (EP-07) ⚠️ |
| `COMPLEX` | Complexidade (média/alta) | Recorte por complexidade (EP-07) ⚠️ |
| `CAR_INT` | Caráter da internação (eletiva/urgência) | Caracterização dos fluxos (EP-07) ⚠️ |
| `VAL_TOT` | Valor total da AIH | Apoio descritivo apenas — fora do eixo principal |

⚠️ = nome/domínio da coluna a **confirmar no dicionário oficial do SIH (grupo RD)** contra o parquet congelado antes de usar — não bloqueia os épicos P0, que dependem só de `MUNIC_RES`/`MUNIC_MOV` + competência.

**Fontes auxiliares:**

| Fonte | Uso | Acesso |
|---|---|---|
| Tabela de municípios IBGE (código → nome) | Traduzir códigos em nomes legíveis | Pública, offline após download |
| Malha município → região de saúde da PB | Base do índice de dependência (EP-03) | Pública (CNES/SAGE/SES-PB) — fonte exata a validar no EP-01 (ver Premissas) |
| GeoJSON dos municípios da PB | Mapa interativo **offline** (RNF-01) | Pública (malhas IBGE), versionada localmente |

**Avaliação de viabilidade:** já validada na prática **para a PB** — os dados de 2025 estão baixados e congelados em parquet no repositório; o fluxo FTP foi comprovado por smoke test. Completude verificada em 22/07/2026: 12/12 meses congelados, 19,2k–23,2k internações/mês (~258k no ano), zero nulos em `MUNIC_RES`/`MUNIC_MOV`; nov/dez na faixa sazonal esperada (comparável a fevereiro).

⚠️ **Exceção (decisão D-1):** a PA-5 (fluxo interestadual) depende de congelamento **adicional ainda não realizado** — RD 2025 de PE, RN e CE (~36 arquivos) do mesmo FTP instável. Essa parte da viabilidade NÃO está validada; risco correspondente registrado em Riscos & dependências.

## Produto final
O que a banca vê no dia 07/08/2026 — dois entregáveis complementares:

**1. Painel interativo (Streamlit)** — demo ao vivo, 100% offline:
- **Mapa interativo O-D** da PB: de onde saem e para onde vão os pacientes, com destaque para os polos concentradores.
- **Matriz origem→destino com filtros** por município/região de saúde e mês.
- **Índice de dependência por região de saúde**, com a definição da métrica legível no próprio painel.
- **Aba de achados & recomendações**: respostas às perguntas analíticas em linguagem executiva + recomendações para a SES-PB ancoradas nos números.

**2. Material de comunicação executiva** (território do Pedro, em `reports/`):
- Narrativa do achado central + recomendações práticas para a SES-PB, em linguagem leiga.
- Apoio de EDA guiada (notebooks do território do Pedro) consolidada em formato apresentável.

Sustentando os dois: o pipeline de congelamento (`src/congelar_sih.py`) como narrativa de atualização mensal — qualquer mês novo publicado pelo DATASUS entra no produto com um comando.

## Escopo
**Em escopo**
- Tratamento e enriquecimento da base SIH-PB 2025 congelada: nomes de municípios (IBGE), mapeamento município → região de saúde da PB, validação de completude dos 12 meses.
- Matriz origem→destino de internações (município × município e agregada por região de saúde).
- Índice de dependência por região de saúde (definição, cálculo, interpretação escrita).
- Resposta às 5 perguntas analíticas com evidência quantitativa.
- Painel Streamlit com mapa interativo e matriz com filtros, rodando 100% offline sobre os parquets do repo.
- Comunicação executiva: narrativa do achado + ≥ 3 recomendações práticas para a SES-PB.
- Reprodutibilidade documentada (`streamlit run` + parquets versionados) e narrativa de atualização mensal via pipeline de congelamento existente (`src/congelar_sih.py`).

**Fora de escopo / não-objetivos**
- Qualquer análise que exija linkage individual sensível (regra fixa do projeto — lição do ENEM).
- Qualquer recorte que já exista em painel público (ex.: contagem simples de internações por município) como produto principal — só como apoio.
- Dados em "tempo real" ou fonte viva na demo — o DATASUS publica lote mensal com ~2 meses de atraso; ritmo mensal é o teto de qualquer produto real, e a demo roda sobre dados congelados.
- Frontend fora do Streamlit (Next.js foi considerado e descartado no briefing): nada de auth, banco de dados, deploy em produção, i18n, SEO.
- Modelagem preditiva/estatística inferencial — a rubrica P3 pede análise consolidada e comunicação, não modelo; horas não cabem nas ~60h.
- Análise de custos/valores de AIH como eixo principal (possível menção descritiva, mas não é o produto).
- Outros estados como unidade de análise (PE/RN/CE entram só como destino de evasão da PB — PA-5).

## Requisitos funcionais
- **RF-01** — Consultar a matriz origem→destino filtrando por município ou região de saúde de origem e por mês. · persona: gestor SES-PB · serve: O2
- **RF-02** — Ver o índice de dependência de cada região de saúde, com a definição da métrica acessível no próprio painel. · persona: gestor SES-PB · serve: O3
- **RF-03** — Visualizar os fluxos de evasão em mapa interativo da PB (origem→destino), com destaque para os polos concentradores. · persona: jornalista de dados / profissional de saúde · serve: O2
- **RF-04** — Ler, no painel, as respostas às perguntas analíticas em linguagem executiva (achado + número + implicação). · persona: professor · serve: O1, O4
- **RF-05** — Ler as recomendações para a SES-PB ancoradas nos achados (cada recomendação aponta para a evidência). · persona: gestor SES-PB · serve: O4
- **RF-06** — Reproduzir o painel do zero a partir do repositório, sem acesso ao DATASUS. · persona: professor · serve: O5
- **RF-07** — Entender a narrativa de atualização mensal: como um mês novo publicado pelo DATASUS entra no produto via pipeline de congelamento. · persona: professor · serve: O1, O5
- **RF-08** — Exportar/citar os números-chave (ex.: tabela da matriz agregada visível e legível para captura ou cópia). · persona: jornalista de dados · serve: O2

## Requisitos não-funcionais
- **RNF-01 — Offline total.** O painel não faz nenhuma requisição externa em runtime (mapas inclusos: geometria/geojson versionado localmente). Critério: demo funciona com rede desligada.
- **RNF-02 — Performance de demo.** Painel carrega em < 10s e cada interação de filtro responde em < 3s no notebook da apresentação (pré-agregação nos dados processados, não cálculo bruto por interação).
- **RNF-03 — Reprodutibilidade.** Dependências pinadas (requirements), parquets congelados versionados, `.dbc`/`.dbf` fora do git; instrução de execução em uma seção do README compreensível por avaliador que nunca viu o repo.
- **RNF-04 — Legibilidade executiva.** Todo texto do painel em pt-BR, sem jargão técnico sem explicação; visualizações com título-afirmação (o achado no título, não "Gráfico 1").
- **RNF-05 — Integridade analítica.** Todo número exibido no painel é derivável dos parquets do repo por notebook/script versionado — nenhum número "mágico" digitado à mão.

## Épicos
> O PM é dono; o scrum-master fatia em stories. Ordenados por prioridade. Fases de projeto de dados, não fatias de web-app.

- **EP-01 — Tratamento e enriquecimento dos dados** · `P0` · serve: O2, O3, O5 · intento (outcome): a dupla trabalha sobre uma base única e confiável — SIH-PB 2025 com nomes de municípios, região de saúde de residência e de internação atribuídas a cada registro (completude dos 12 meses já verificada no congelamento).
- **EP-02 — Análise origem→destino** · `P0` · serve: O2 · intento (outcome): qualquer pergunta "de onde vem / pra onde vai" tem resposta numérica validada — matriz O-D por município e por região, taxas de evasão, e as perguntas PA-1, PA-3, PA-4 e PA-5 respondidas com evidência.
- **EP-03 — Índice de dependência por região de saúde** · `P0` · serve: O3 · intento (outcome): o gestor da SES-PB lê um número por região e entende, sem ajuda, o quanto aquela região depende de fora para internar seus residentes (PA-2 respondida; fórmula definida, calculada e interpretada por escrito).
- **EP-04 — Painel Streamlit** · `P0` · serve: O1, O2, O3 · intento (outcome): o professor assiste a uma demo fluida e offline em que o gestor simbólico navega mapa e matriz com filtros e chega ao achado principal em menos de um minuto de interação.
- **EP-05 — Comunicação executiva & recomendações** · `P0` · serve: O4, O1 · intento (outcome): quem assiste à apresentação sai sabendo o achado central e o que a SES-PB deveria fazer a respeito — narrativa executiva + ≥ 3 recomendações ancoradas em evidência, no painel e no material de apresentação (território do Pedro em reports/, com EDA guiada).
- **EP-06 — Reprodutibilidade & narrativa de atualização** · `P1` · serve: O5, O1 · intento (outcome): o avaliador reproduz o painel numa máquina limpa sem tocar no DATASUS, e entende como um mês novo entraria no produto — a prova material da "viabilidade real".
- **EP-07 — Aprofundamentos analíticos** · `P2` · serve: O2, O4 · intento (outcome): se sobrar hora, a análise ganha um segundo eixo que enriquece as recomendações (ex.: recorte por especialidade/complexidade da internação, caracterização dos pares O-D mais intensos) — sem nunca competir com os P0.

## Plano de execução
> 22/07 → 07/08/2026 (16 dias, ~60h de dupla). Augusto na frente técnica; Pedro entra em paralelo (EDA guiada + `reports/`) assim que a base tratada existir. Datas são janelas-alvo por épico — o fatiamento fino é do backlog. Os últimos dias são folga deliberada para ensaio da demo.

| Etapa | Atividade | Épico | Prazo | Quem |
|---|---|---|---|---|
| 1. Base confiável | Enriquecer SIH-PB 2025 (nomes IBGE, malha região de saúde), confirmar colunas ⚠️ no dicionário RD | EP-01 | 22–25/07 | Augusto |
| 2. Análise O-D | Matriz origem→destino (município e região), taxas de evasão, responder PA-1, PA-3, PA-4, PA-5 | EP-02 | 25–29/07 | Augusto |
| 3. Índice de dependência | Definir fórmula (validar no gate do backlog), calcular por região, interpretação escrita (PA-2) | EP-03 | 28–30/07 | Augusto |
| 4. EDA guiada + narrativa | EDA nos notebooks do território do Pedro sobre a base tratada; rascunho da narrativa executiva e das recomendações em `reports/` | EP-05 | 26/07–03/08 | Pedro (guiado) |
| 5. Painel Streamlit | Mapa interativo offline, matriz com filtros, aba do índice, aba de achados/recomendações | EP-04 | 30/07–04/08 | Augusto |
| 6. Reprodutibilidade | Requirements pinados, README de execução, teste em máquina limpa, narrativa de atualização mensal | EP-06 | 04–05/08 | Augusto |
| 7. Consolidação & ensaio | Fechar recomendações no painel + `reports/`, ensaio completo da demo offline, ajustes finais | EP-05 + folga | 05–06/08 | Dupla |
| 8. Apresentação | Demo ao vivo da P3 | — | **07/08** | Dupla |

EP-07 (`P2`) não tem janela reservada: só entra se alguma etapa terminar antes do prazo, e nunca depois de 04/08.

## Premissas
- **Troca de projeto será formalizada** com o professor antes do investimento pesado de horas (ele já sinalizou aceite verbal). Se recusar, este PRD é descartado.
- **A malha de regiões de saúde da PB é obtenível de fonte pública** (CNES/SAGE/mapa da SES-PB) e mapeável por código IBGE de município. Se a fonte oficial for ambígua, adotaremos a divisão em macro/regiões mais recente documentando a escolha.
- **Janela jan–dez/2025 fechada.** Volumes mensais na faixa 19,2k–23,2k sem cratera de subnotificação; dezembro pode ainda receber retificações do DATASUS (AIH atrasada) — declarado como nota metodológica, sem exclusão de meses.
- **`MUNIC_MOV` é interpretado como município do estabelecimento de internação** (proxy de destino do paciente). Limitações conhecidas do SIH (AIH ≠ paciente único, reinternações) serão declaradas na seção de limitações, não corrigidas por linkage.
- **O índice de dependência será definido pela dupla** (ex.: % de internações de residentes da região realizadas fora dela), pois não há fórmula oficial pactuada no briefing — a definição exata é decisão de análise a validar no gate do backlog.
- **A demo roda em máquina local da dupla** — nenhum deploy/hospedagem é necessário para a P3.

## Riscos & dependências
- **Prazo: 16 dias, ~60h de dupla, com apenas ~metade das horas técnicas (Augusto).** Mitigação: EP-07 é o único P2 e é a válvula de escape; corte dele primeiro.
- **Mapeamento município→região de saúde**: fonte pública pode estar desatualizada ou divergente entre órgãos; escolha errada distorce o índice de dependência (o produto central). Validar cedo, dentro do EP-01.
- **Geometria do mapa offline**: mapa interativo bonito e offline no Streamlit exige geojson local e biblioteca adequada; risco de sumidouro de horas de visual. Guard-rail do briefing: "sem virar projeto de frontend".
- **Dependência da colaboração assíncrona com Pedro** (não-técnico, GitHub Desktop, só `main`): EP-05 depende do território dele; os épicos técnicos (EP-01–04) não podem bloquear nele.
- **Congelamento PE/RN/CE (decisão D-1, sustenta a PA-5)**: reabre a dependência do FTP instável do DATASUS que o congelamento da PB tinha eliminado — ~36 arquivos novos, dentro da janela de 16 dias. Mitigação: guard-rail de degradação na US-08 (se o congelamento não fechar no prazo, PA-5 reduz para nota metodológica).

## Autoavaliação (handoff)
- **Parte mais fraca:** a definição do índice de dependência (EP-03) está delegada a uma premissa — é o produto-assinatura do projeto e ainda não tem fórmula fechada. Se a definição escolhida for questionável, o diferencial inteiro enfraquece.
- **O que mais reduziria a incerteza:** validar cedo a fonte da malha município→região de saúde da PB — ela sustenta o índice de dependência, o produto-assinatura.
- **O que ainda depende de suposição:** o aceite formal do professor à troca de projeto; a existência de um mapeamento público confiável município→região de saúde da PB; as colunas do layout RD marcadas com ⚠️ (nome/domínio a confirmar no dicionário); e as metas numéricas de performance da demo (RNF-02), fixadas por bom senso, não por medição.
