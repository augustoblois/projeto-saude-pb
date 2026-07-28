# STATUS — Projeto Saúde (Mapa de Evasão Assistencial da PB)

> **Pedro: este arquivo é pra você.** Sempre que abrir o projeto: GitHub Desktop → botão **Pull** (puxa as novidades) → ler este arquivo. Ele diz onde o projeto está, o que mudou e o que você pode fazer agora. O Augusto atualiza toda vez que trabalha no projeto.

## Onde estamos (27/07/2026)

- **Tema fechado:** vamos mapear de onde saem e pra onde vão os pacientes que internam na Paraíba — quem precisa viajar pra outra cidade pra conseguir internação, e quais regiões dependem de quais. O resultado final vai ser um painel interativo (um site simples feito em Python).
- **Todos os dados de 2025 já estão no projeto:** os 12 meses de internações da PB, direto do sistema do Ministério da Saúde (DATASUS). São **cerca de 258 mil internações no ano** (entre 19 mil e 23 mil por mês), conferidas uma a uma: nenhuma linha com informação faltando nas colunas que importam. O achado que motiva tudo segue de pé: **quase metade dos pacientes interna fora da cidade onde mora**.
- **O plano do projeto inteiro está escrito, revisado e aprovado** — o que vamos analisar, em que ordem, e quem faz o quê até a apresentação. Os documentos vivem na pasta `docs/` (você não precisa ler; sua referência é este arquivo).
- **Decisões já fechadas e registradas:** painel em **Streamlit** (ferramenta de Python que transforma análise em site interativo); os **paraibanos internados em outros estados** (PE/RN/CE) entram na análise; e o **índice de dependência** — o número principal do projeto — é a porcentagem dos moradores de cada região que precisou internar FORA da própria região.
- **A análise central do projeto está pronta:** cada internação sabe a qual "região de saúde" pertence (a divisão oficial do SUS — a PB tem 16), e já existe a **matriz origem→destino** — a tabela que diz, de cada cidade e de cada região, quantos pacientes foram internar em cada outra, mês a mês. É o coração do projeto: tudo daqui pra frente (análises, índice, painel) consome essa matriz.
- **O número principal do projeto mudou de 47,8% pra 49,8%** (internações de jan/2025 fora do município de residência). O 47,8% veio da fase de pesquisa e não tinha memória de cálculo; ao refazer a conta com a base congelada — de cinco jeitos diferentes — o resultado é 49,8%, sempre. Adotamos o número que conseguimos provar. No ano fechado: **50,5% das internações são fora do município onde o paciente mora**.
- **Também já sabemos quantos paraibanos internaram FORA do estado em 2025: 3.682** (a maioria em Pernambuco e no Rio Grande do Norte). Baixamos os dados dos 3 estados vizinhos e filtramos só quem mora na PB. É pouco perto das 258 mil internações internas — sinal de que o problema de "viajar pra internar" acontece quase todo DENTRO do estado.
- **As cinco análises principais do projeto estão prontas e conferidas.** Em uma linha cada: os pacientes que saem da própria cidade se concentram em **João Pessoa e Campina Grande (58,6% do movimento)**; **cidade pequena perde muito mais** (até 10 mil habitantes, 98% dos moradores internam fora; acima de 100 mil, só 9%); os **caminhos não mudam** ao longo do ano (13 dos 20 trajetos mais usados aparecem nos 12 meses); quem **sai do estado** são 3.682 pessoas (1,41%), por dois motivos que convivem — estar na divisa e buscar tratamento grave — sem que dê pra dizer quanto é de cada; e **8 das 16 regiões de saúde passam de 50%** de dependência.
- **Toda a parte de análise do projeto está concluída.** Do dia 25/07 em diante não há mais conta a fazer: o que falta é montar o painel (o site interativo) e escrever o texto de recomendações para a apresentação.
- **O painel saiu do papel e já roda na máquina.** Ele tem quatro abas previstas; **três já funcionam**: a tabela de quem vai de onde pra onde, o **mapa da Paraíba** e o **ranking do índice de dependência**. Só a última (os achados e recomendações) ainda está vazia — e ela depende do texto que a gente ainda vai escrever.
- **O mapa mostra uma coisa que ninguém tinha desenhado ainda:** cada cidade da Paraíba está pintada com a cor da cidade para onde a maioria dos seus moradores acaba internada. O resultado é um mapa de "territórios": dá pra ver no olho o **território de Campina Grande (62 cidades), o de João Pessoa (48) e o de Patos (30)**.
- **Prazo:** apresentação dia 07/08/2026 (13 dias).

## O que aconteceu na última sessão (27/07/2026)

**A parte técnica do projeto está 100% encerrada. Esta sessão criou a camada de preparação para a apresentação: um plano de estudos pra você dominar o projeto inteiro até o dia 07/08.**

O projeto já tinha todas as análises prontas, o painel rodando, a narrativa escrita — e isso estava registrado como "completo". Mas faltava uma coisa: como você e o Augusto dominam tudo o que foi feito, E2E, até dia 07/08? Que forma de estudar não deixa ninguém pra trás? Essa sessão resolveu isso com três documentos novos.

### Planos de estudo — divisão estratégica

**O QUÊ:** Três arquivos novos em `docs/`:

1. **`plano-estudos.md`** — plano mestre: explica o princípio da divisão e o cronograma conjunto dos 10 dias (28/07 a 06/08, 2 horas por pessoa por dia). Inclui a tabela das 8 armadilhas de número que os dois precisam decorar, e um banco de 15 perguntas prováveis da banca com o dono de cada resposta.

2. **`plano-estudos-augusto.md`** — trilha do Augusto, dia a dia: "como o número nasce" (origem dos dados, tratamento, região de saúde, matriz origem→destino, índice de dependência, o painel, como rodar novamente). Autocontida, sem depender de ler outra coisa. Inclui glossário de 15 termos técnicos.

3. **`plano-estudos-pedro.md`** — trilha sua, dia a dia: "o que o número quer dizer" (os 7 achados, as 5 recomendações, as 9 limitações, o sumário de evidências, o painel como gestor vê). Autocontida. Primeiro dia tem o teste do mapa que estava pendurado.

**POR QUÊ:** O projeto foi dividido em duas metades simétricas (mesma dificuldade, mesmos dias de estudo). No dia 04/08 você dois se ensinam: cada um dá uma aula de 30 minutos da própria metade pro outro, sem consultar arquivo. Depois (06/08, critério de aprovação) cada um responde 3 perguntas sobre a metade do outro. Esse mecanismo faz vocês dois terminarem sabendo o projeto inteiro sem que os dois estudem tudo do zero — ganha tempo, e a aula mútua fixa o conhecimento melhor que qualquer revisão sozinho.

**DESOBSTRÓI:** O teste de leitura do mapa (US-12, que ficou pendurado desde a Etapa 16) agora está agendado para 28/07 — seu primeiro dia. E o ensaio da demo (US-17, que também estava pendurado) é nos dias 05 e 06/08, quando vocês dois já dominam cada metade.

**ONDE:** `docs/plano-estudos.md`, `docs/plano-estudos-augusto.md`, `docs/plano-estudos-pedro.md`

### Atualizações menores

- **`CLAUDE.md`** — a regra de linguagem do STATUS.md foi revisada. Antes dizia "linguagem leiga — Pedro não é técnico"; agora diz "sem jargão — todo termo que nasce aqui dentro chega nele sem contexto e vai explicado em uma frase". É regra sobre o texto, não sobre o leitor. (O Augusto corrigiu o enquadramento — vocês dois são competentes, só não participam um da conversa do outro.)
- **`docs/definicao-indice-dependencia.md`** — remoção de frases sobre o leitor que entraram em decisão anterior; justificativa agora foca no custo real (história assíncrona é lenta).

*(O detalhe de como cada uma das 23 etapas anteriores funcionou está em `docs/diario-do-projeto.md`.)*

## Pra você, Pedro

### Novo: plano de estudos feito para você (28/07–06/08)

**Está pronto:** `docs/plano-estudos-pedro.md`

Cronograma de 10 dias, 2 horas por dia — autocontido, não depende de ler mais nada. Começa do que o número quer dizer (os 7 achados principais do projeto, as 5 recomendações, as 9 limitações), passa pelo sumário de evidências (saber de cor que número saiu de onde), explica o painel como você vai apresentar, e termina no ensaio da demo.

**Estrutura:**
- **28/07 (dia 1):** leitura dos achados + teste do mapa (1 minuto, esse combinado antigo que ficava pendurado — agora agendado).
- **29–31/07 e 01–03/08:** um tópico por dia (narrativa, painel, limitações, etc.).
- **04/08:** vocês dois se ensinam — você faz uma aula de 30 minutos contando os achados e recomendações do projeto pro Augusto, sem consultar arquivo. Depois ele faz o dele com você (a metade técnica).
- **05–06/08:** ensaio da demo com os dois — ele apresenta, você observa; depois trocam. Corrigem o que ficar confuso.

**Também neste arquivo:** as 8 armadilhas de número pra decorar (tipo: "50,5% é fora do município; 26,4% é dependência regional — são contas diferentes"), e as 15 perguntas prováveis da banca com o dono de cada resposta (quem do projeto responde melhor: você ou Augusto).

**Igualmente importante:** existe um plano mestre em `docs/plano-estudos.md` que explica por que essa divisão funciona — se quiser entender a lógica do que estão fazendo, começa por lá. Mas pra estudar em si, `plano-estudos-pedro.md` é autocontida.

### Teste do mapa — agendado para amanhã (28/07)

1. Terminal na pasta: `streamlit run app.py`
2. Navegador abre. Clique em **Mapa**.
3. Olhe por 1 minuto, sem ajuda. Depois diga: **quais são as cidades que puxam pacientes de toda a Paraíba?**

Se as duas principais saltarem aos olhos, passou. Se precisar procurar, o mapa está errado — corrijo antes de 07/08. Me responde por WhatsApp.

### Novo notebook de estudo: exploração da base (opcional)

**Está pronto:** `notebooks/90-eda-guiada.ipynb`

Se quiser entender de verdade os dados (não obrigatório pro plano de estudos acima, mas valioso): começa do básico e vai até as 16 regiões. Cada trecho tem explicação em português. Tem 3 momentos onde você coloca informação (sua cidade, comparação, sua região) e roda.

Todos os 34 números foram conferidos contra as tabelas prontas — bateram todos. Achado importante registrado lá: das 223 cidades da PB, só 62 têm internação SUS; as outras 161 aparecem com 100% de evasão porque não têm hospital, não porque perdem pacientes.

### Já enquanto estiver no painel: explore as abas

**Índice de dependência:** ranking das 16 regiões. Se perguntarem "o que é esse índice?", clique em um bloco e leia a definição direto do painel — está tudo ali.

**Achados & recomendações:** os 7 achados com números, as 5 recomendações. É o lugar onde tudo converge — vai dar segurança pra você ver tudo de uma vez.

**Sobre os dados:** de onde vêm os números, por que funcionam sem internet, como atualizar com dados novos. Resguarda a pergunta que o professor provavelmente fará.

### Leitura importante: narrativa do projeto

Abra `reports/narrativa-executiva.md`.

É o texto da apresentação em uma página: achado central, 7 achados, 5 recomendações, fecho, limitações. **É exatamente o que você vai contar no dia 07/08, com números ao lado.**

Se algo ficar confuso, fala pro Augusto — com 10 dias ainda dá tempo de reescrever.

### Familiarização rápida com os números (opcional)

**Caminho mais curto:**
1. **`docs/diario-do-projeto.md`** — história do projeto inteira, etapa por etapa. Rende mais por minuto.
2. **Tabelas:** `data/processed/indice_dependencia_regional.csv` (índice das 16 regiões) e `outputs/tables/pa3_saldo_municipios.csv` (saldo por cidade). Olhar os números com os olhos gruda.
3. **Gráficos em `outputs/figures/`** — as imagens que vão pro slide.

### Explorar a base de dados em profundidade (opcional)

Se quiser mergulhar nos dados:

1. **Setup (uma vez só):** terminal na pasta, rodar: `pip install -r requirements.txt`
2. **Jupyter:** `jupyter notebook`, novo notebook:
   ```python
   import pandas as pd
   df = pd.read_parquet("data/processed/sih_pb_2025_regioes.parquet")
   ```
   Cada linha = uma internação. Úteis: `nome_mun_res` (onde mora), `nome_mun_mov` (onde internou), `regiao_res` / `regiao_int`. Quando residência ≠ internação = viajou.

3. **Roteiros prontos:**
   - `notebooks/01-tratamento-base.ipynb` — como os dados foram feitos.
   - `notebooks/01-regiao-saude.ipynb` — como a região foi colocada.
   - `notebooks/01-matriz-od.ipynb` — como a matriz foi montada.
   - `docs/dicionario-dados.md` — o que cada coluna significa.

4. **Salvar:** novo notebook em `notebooks/` com nome começando em `90-`, ex: `90-eda-pedro.ipynb`. Perguntas boas: quais cidades mais mandam pacientes pra fora? Pra onde? Quais regiões mais perdem?

5. **Terminar:** GitHub Desktop → Commit → Push.

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
