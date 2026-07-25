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

## Etapa 6 — US-02: região de saúde em cada internação ✅
**O QUE:** Atribuímos a cada uma das 258.125 internações a região de saúde de residência (`regiao_res`) e a de internação (`regiao_int`), usando a base territorial oficial do DATASUS (`ftp.datasus.gov.br/territorio/tabelas/2025/10-base_territorial_out25.zip`, baixada em 23/07/2026) — a mesma relação município→região que o TabWin do Ministério usa. Residentes de outros estados (1.502 internações, maioria PE/RN) marcados "Fora da PB".
**POR QUÊ:** A matriz O-D e o índice de dependência — o produto do projeto — são por região de saúde (16 na PB), a unidade de planejamento da Secretaria. Validações: 223 municípios cobertos, 1 região cada; zero linhas perdidas; zero nulos. Primeiro retrato: região de João Pessoa 41,3% + Campina Grande 26,4% ≈ ⅔ das internações do estado. Aprovado em revisão independente que refez as contas do zero.
**ONDE:** `notebooks/01-regiao-saude.ipynb`, `src/baixar_base_territorial.py`, `data/processed/regioes_saude_pb.csv`, `data/processed/sih_pb_2025_regioes.parquet`

## Etapa 7 — US-04: matriz origem→destino ✅
**O QUE:** Construímos a matriz O-D: internações contadas por (município residência × município internação × mês) e por (região × região × mês), com flag de evasão e taxas de evasão por região de origem. Validação-âncora jan/2025: volume bateu exato (20.029); a taxa recalculada deu **49,8%, não os 47,8% do PRD** — investigamos 5 variantes de cálculo (inclusive a pegadinha `UF_ZI` do SIH), nenhuma reproduz o número antigo (fase de pesquisa, sem código rastreável), e **adotamos 49,8%** — corrigido em PRD/briefing/backlog. Ano fechado: evasão municipal 50,5%; extremos regionais 1,8% (região de JP) vs 84,5% (3ª região); top fluxo Santa Rita→JP (5.645).
**POR QUÊ:** A matriz é o coração do produto — análises PA-1..PA-4, índice de dependência e painel consomem essas agregações, não a base linha-a-linha. Aprovada em revisão independente que refez todas as contas do zero.
**ONDE:** `notebooks/01-matriz-od.ipynb` (§4 = investigação da divergência), `data/processed/matriz_od_municipal_mensal.parquet`, `matriz_od_regional_mensal.csv`, `taxas_evasao_regional.csv`

## Etapa 8 — US-08 (parte 1): paraibanos internados fora do estado ✅ (congelamento)
**O QUE:** Estendemos o pipeline (`src/congelar_sih_vizinhos.py`) pra baixar os 12 meses de 2025 de PE/RN/CE (~1,9 mi de internações), filtrar residentes da PB e congelar um parquet enxuto: **3.682 internações** (PE 2.147, RN 1.359, CE 176). Validado: 36/36 arquivos, 100% residentes PB, 12 meses sem buracos.
**POR QUÊ:** Os arquivos do SIH são organizados pela UF do hospital — paraibano internado em Recife está no arquivo de PE. Sem esse passo, a evasão interestadual (PA-5) seria invisível. Achado preliminar: volume ~1,4% do interno → a evasão da PB é quase toda dentro do estado. Falta a parte 2: análise PA-5 (% e recorte de fronteira).
**ONDE:** `src/congelar_sih_vizinhos.py`, `data/raw/sih_pb_residentes_fora_2025.parquet`

## Etapa 9 — US-05: PA-1, concentração de destino ✅
**O QUE:** Agrupamos as 130.379 internações de não-residentes pelo município do hospital, com percentual acumulado. **JP 33,5% + CG 25,2% = 58,6%**; com Patos, 67,2%; 7 municípios = 80% do fluxo. Achado não previsto: **só 62 dos 223 municípios da PB registraram alguma internação SUS em 2025**. Robustez: excluir residentes de outros estados move 0,1 p.p. (58,5%); mês a mês a fatia dos polos nunca cai de 56% (oscila 56,6%–61,3%).
**POR QUÊ:** É a prova de que a rede é **funil, não malha** — sustenta a recomendação de regionalização. Os dois testes extras existem para blindar contra as objeções óbvias da banca ("e se for efeito de gente de fora?" / "e se for sazonal?").
**ONDE:** `notebooks/01-pa1-concentracao.ipynb`, `outputs/tables/pa1_ranking_destinos.csv`, `outputs/figures/pa1_concentracao_destino.png`

## Etapa 10 — US-06: PA-3, evasão × porte do município ✅
**O QUE:** Cruzamos a taxa de evasão de cada município com sua população (estimativa IBGE congelada em CSV, `src/baixar_populacao_ibge.py`). Queda monotônica: **98,1%** (≤10 mil hab., 140 cidades) → 80,4% → 64,9% → 53,0% → **9,3%** (>100 mil, 4 cidades). **133 das 140 cidades pequenas têm evasão de exatamente 100%** — não internaram nenhum morador no ano. Saldo (recebidos − enviados): JP **+41.761**, CG **+32.233**.
**POR QUÊ:** Muda o enquadramento político da conclusão: não é má gestão municipal, é impossibilidade estrutural — cidade pequena não sustenta hospital. A solução tem que ser regional. Armadilha resolvida: código IBGE do SIH tem 6 dígitos e o do IBGE tem 7 (o último é verificador); o join reaproveita a solução da US-01 — 223/223, zero órfãos.
**ONDE:** `notebooks/01-pa3-porte.ipynb`, `src/baixar_populacao_ibge.py`, `outputs/tables/pa3_*.csv`, `outputs/figures/pa3_evasao_x_porte.png`

## Etapa 11 — US-07: PA-4, estabilidade temporal ✅
**O QUE:** Medimos quantos meses cada par origem→destino do top 20 anual permanece no top 20 mensal. **13 dos 20 pares aparecem nos 12 meses**; sobreposição média 17,1/20 (85%); Spearman mês×ano entre 0,908 e 0,950. A instabilidade fica nas posições 14–20, onde 3–4 casos mudam o ranking.
**POR QUÊ:** Define a natureza da recomendação. Fluxo **estrutural** = pode ser pactuado na PPI com números fixos; fluxo conjuntural exigiria outra política. Achado de processo: um código IBGE hardcoded errado (250190 = Belém/PB em vez de 250180 = Bayeux) foi pego por `assert` — o código era de município **real**, então sem o assert teria passado silencioso.
**ONDE:** `notebooks/01-pa4-estabilidade.ipynb`, `outputs/tables/pa4_*.csv`, `outputs/figures/pa4_estabilidade_fluxo.png`

## Etapa 12 — US-08 (parte 2): PA-5, análise do fluxo interestadual ✅
**O QUE:** Sobre os 3.682 residentes PB internados em PE/RN/CE. Denominador correto = residentes PB internados na PB (256.623) + fora (3.682) = 260.305 → **1,41%** (o denominador ingênuo, 258.125, misturaria não-residentes). Destinos: Recife 41,3%, **Alexandria/RN 23,3%** (2º — hospital regional que atende o sertão da divisa; investigado, achado genuíno), Natal 9,3%. Fronteira via proxy de distância entre centroides (não há malha de polígonos no repo), corte de 20 km declarado como arbitrário.
**POR QUÊ:** Separa "pegou o hospital mais perto" de "atravessou o estado atrás de alta complexidade". **O achado robusto é a razão, não a fração:** o grupo do interior tem taxa de alta complexidade 1,7× a 2,8× maior que o da fronteira em **todos** os cortes testados (10–30 km), e custo médio o dobro (R$ 5.061 vs R$ 1.992). A fração de volume (42%/58%) é frágil — varia de 11,5% a 58,5% conforme o corte, e chega a inverter. Na apresentação: usar a razão, nunca cravar a fração.
**ONDE:** `notebooks/01-pa5-interestadual.ipynb`, `outputs/tables/pa5_*.csv`, `outputs/figures/pa5_*.png`

## Etapa 13 — US-10: índice de dependência calculado (US-09 em aberto) ✅⚠️
**O QUE:** Índice para as 16 regiões = % das internações de residentes da região realizadas fora dela (decisão D-2). **8 das 16 acima de 50%** → hipótese PA-2 (previa ≥ 1/3, registrada no PRD antes do cálculo) **confirmada**. Extremos: 3ª Região 84,5%; 1ª (JP) 1,8%; 16ª (CG) 4,1%. Validação por **3 caminhos independentes** (matriz regional, matriz municipal remapeada do zero, base linha a linha por AIH) + o CSV pré-existente: delta 0,0 nos três pares, com asserts.
**POR QUÊ:** É o diferencial do projeto — não existe em painel público. A tripla validação existe porque um número que ninguém mais publica não tem com o que ser comparado externamente; a única defesa é a consistência interna. **US-09 seguia aberta** neste momento: faltava o teste de leitura com o Pedro (ação humana) — resolvido na Etapa 14.
**ONDE:** `docs/definicao-indice-dependencia.md`, `notebooks/01-indice-dependencia.ipynb`, `data/processed/indice_dependencia_regional.csv`, `outputs/figures/indice_ranking_dependencia.png`

## Marco (24/07) — troca de projeto formalizada com o professor ✅
**O QUE:** E-mail enviado ao professor formalizando a substituição do projeto do ENEM pelo Mapa de Evasão Assistencial da PB — **e respondido com aceite no mesmo dia**. Encerra o gap G-4, aberto desde o início do planejamento.
**POR QUÊ:** Era o único evento capaz de invalidar todo o escopo — o aceite havia sido apenas verbal, e o investimento pesado de horas já estava em curso. Com o aceite por escrito, a cadeia de planejamento (briefing → PRD → backlog) deixa de rodar sobre suposição.
**ONDE:** `TASKS.md` (G-4), `docs/briefing.md`, `docs/prd.md`, `docs/backlog.md`

## Etapa 14 — US-09: definição do índice fechada e auditada ✅
**O QUE:** Fechamos a definição escrita do índice (fórmula, exemplo passo a passo da 3ª Região, leitura leiga, faixas com corte justificado, 6 limitações). Auditamos **os 12 números do texto recalculando cada um do zero pela base linha a linha** — bateram todos. Atualizamos a limitação (a): o buraco "hospitais fora da PB" deixou de ser estimativa e virou número medido — **3.682 internações = 1,41%** do total de paraibanos (3.682 de 260.305).
**POR QUÊ:** Este texto é o que aparece no painel — é o que faz um gestor confiar no número-assinatura do projeto. A auditoria numérica existe porque o risco real aqui não é errar a conta, é o texto envelhecer em cima de uma conta certa: a limitação (a) ainda dizia "levantamento em andamento, ~1,4% não validado" **depois** da US-08 ter fechado com 1,41%. Foi exatamente o padrão que derrubou 4 das 5 análises na revisão (ver nota de método abaixo). Sobre o fluxo interestadual, o texto deliberadamente **não crava** a divisão fronteira × interior: ela varia de 11,5% a 58,5% conforme o corte de distância e chega a inverter — o que é estável é a razão de complexidade (interior 36,2% de alta complexidade vs. 13,1% na fronteira).
**ONDE:** `docs/definicao-indice-dependencia.md` (§6a reescrita), `TASKS.md`, `docs/backlog.md`
**DECISÃO:** o teste de leitura com o Pedro deixou de bloquear o fechamento (chamada do Augusto, que leu o texto e julga a legibilidade suficiente — o Pedro é leigo em dados e ferramenta, não em raciocínio). O roteiro de 7 perguntas fica no doc como ferramenta opcional. Vale **só para a US-09**: os testes de leitura da US-12 (mapa) e US-16 (narrativa) seguem valendo como aceite.

## Etapa 15 — US-11: painel Streamlit no ar, aba da matriz O-D ✅
**O QUE:** Primeira aba do painel (`app.py`): matriz origem→destino com filtro de origem e de mês, alternando entre município e região de saúde. O painel abre em 6,4s e cada filtro responde em milissegundos, porque ele **só lê as tabelas já somadas** pelos notebooks — nunca recalcula a base de 258 mil internações durante a interação. Números conferidos por dois caminhos independentes: jan/2025 = 20.029 internações / 49,8% de evasão (igual à US-04) e o índice das 16 regiões refeito pelo caminho do app bate com a US-10 em 16/16.
**POR QUÊ:** É a vitrine do projeto — o que o avaliador vê no dia 07/08. A separação "notebook calcula, painel só exibe" é o que garante a demo offline e sem travar: qualquer conta pesada feita ao vivo seria risco na apresentação.
**ONDE:** `app.py`, consome `data/processed/matriz_od_{municipal,regional}_*`

## Etapa 16 — US-12: mapa das áreas de captação (aguardando teste do Pedro) ⚠️
**O QUE:** Aba do mapa: os 223 municípios da PB desenhados a partir de malha do IBGE congelada no repo (`outputs/malha_municipios_pb.geojson`, 200 KB), com linhas ligando os maiores fluxos e marcadores nos polos. Zero mapa de fundo baixado da internet — o painel roda com a rede desligada.
**POR QUÊ / DECISÃO (guard-rail do backlog):** o plano previa colorir os municípios pela **taxa de evasão**. Ao construir, o dado mostrou que essa cor não informa nada: a **mediana da taxa de evasão municipal é 100%** e 173 dos 223 municípios passam de 90% — o mapa virava um bloco de uma cor só. Trocamos a cor para o **destino principal de cada município**, e o mapa passou a mostrar as **áreas de captação**: dá para ver o território de Campina Grande (62 municípios), o de João Pessoa (48), o de Patos (30). Continua sendo um coroplético, então o guard-rail está respeitado. O achado por trás disso entra na narrativa: os 50,5% de evasão não são escolha por hospital melhor, são **ausência de leito na origem**.
**ACHADO DE PROCESSO:** o mapa passou em todos os testes automáticos — números certos, coordenadas certas, tempos ótimos, nenhuma exceção — e mesmo assim renderizava um bloco sólido na tela. Causa: a malha do IBGE lista os pontos de cada município no sentido anti-horário (o padrão do formato GeoJSON), mas a biblioteca de desenho do Plotly lê polígonos sobre a esfera, onde esse sentido significa "todo o globo **menos** este município". Corrigido no congelamento do arquivo, com o motivo documentado e **uma validação automática** que reprova se alguém regravar no sentido errado. Lição: teste automático confirma que o código roda, não que o desenho está certo — só abrir no navegador pega isso.
**PENDENTE:** teste de leitura com o Pedro (critério de aceite desta story, mantido pela decisão da Etapa 14): ele precisa olhar o mapa por 1 minuto e nomear os polos sem ajuda.
**ONDE:** `app.py` (aba Mapa), `src/baixar_malha_pb.py`, `outputs/malha_municipios_pb.geojson`, `outputs/centroides_municipios_pb.csv`

---

*Nota de método (vale pra apresentação):* as cinco análises foram construídas em paralelo e cada uma passou por revisão independente que refez as contas do zero. Quatro voltaram reprovadas na primeira rodada — e **nenhuma reprovação foi erro de cálculo**: em todos os casos o número estava certo e o texto ao redor dele estava desatualizado ou afirmava mais do que o dado sustentava (título dizendo "sete" com oito barras no gráfico; conclusão contradita pela tabela logo acima; número de validação não derivável). O padrão: texto escrito antes da execução final e nunca reconferido.

*Próximas etapas previstas (ordem do backlog): painel Streamlit (US-11..14) → narrativa executiva e recomendações (US-16). Com o EP-03 fechado, todo o trabalho analítico do projeto está concluído — o que resta é vitrine (painel) e comunicação.*
