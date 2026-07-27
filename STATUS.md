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

**Três stories de entrega foram completadas — análise encerrada, agora é reprodutibilidade e material de estudo.**

Até ontem, o projeto afirmava estar "100% completo" — e estava, em análise. Mas faltava a camada de entrega: como alguém clona o projeto daqui a 3 meses e rodas tudo novamente sem quebranto? Como o Pedro se estuda sem precisar de aulas? Como atualizar com dados de agosto? Essa sessão fechou os 3 vazios.

### US-15: Notebook de estudo para o Pedro

**O QUÊ:** Novo arquivo `notebooks/90-eda-guiada.ipynb` — um roteiro em 9 seções que sai do básico ("o que é uma linha desses dados?") até as 16 regiões. Cada pedaço de código vem com explicação em português antes. Tem 3 momentos onde o Pedro coloca informação dele e roda: a cidade dele, comparar duas cidades, a região dele.

**POR QUÊ:** É o material de estudo dele antes de apresentar no dia 07/08. Parece óbvio ("lê o notebook"), mas a experiência de clonar um projeto de dados e rodar o primeiro notebook sem entender nada é sufocante. Este notebook é feito sob medida pra ele: começa do zero, explica cada passo em português, e os resultados mostram números que interessam (_quanto de evasão tem na sua cidade?_). Se ele digitar um nome que não existe, não aparece um erro feio — aparece uma mensagem orientando a conferir a grafia.

**Qualidade:** Todos os 34 números do notebook foram conferidos contra os relatórios e tabelas já prontas — **bateram todos**. Dois números que parecem erro e não são ficaram explicados dentro do notebook — o mais interessante: **161 cidades da PB aparecem com 100% de evasão, e 161 é exatamente 223 menos 62**. Das 223 cidades do estado, só 62 têm alguma internação registrada; as outras 161 não têm leito de SUS. Um "ranking de evasão" nessas cidades não mede acesso à saúde, mede se a cidade tem hospital.

**Figuras:** Quatro novas em `outputs/figures/` (nomes começando com `eda_`), cada uma com o achado escrito no próprio título.

**ONDE:** `notebooks/90-eda-guiada.ipynb`, `outputs/figures/eda_*.png`

### US-18: Reprodução em máquina limpa

**O QUÊ:** O `README.md` foi reescrito para levar alguém que nunca viu o projeto do zero até o painel aberto — antes ele nem mencionava o comando que abre o painel. Versões de todos os programas que o projeto usa foram fixadas no `requirements.txt`, para que quem instalar daqui a meses receba exatamente as mesmas versões testadas.

**A questão crítica:** nesta story, a gente descobriu um problema sério. Um dos notebooks buscava um arquivo no site do Ministério da Saúde em vez de usar uma cópia local — o arquivo é só 1,6 MB (base territorial = a tabela que mapeia cada município pra sua região de saúde), mas viola a regra número 1 do projeto: **nada na apresentação depende de fonte viva**. Se no dia 07/08 a internet falhar ou o site mudar, o notebook quebrava.

**Correção:** O arquivo (`data/raw/base_territorial_out25.zip`) agora é guardado junto com o projeto. Todos os 9 notebooks foram reexecutados **com a internet bloqueada de propósito** — todos rodaram até o fim sem tentar acessar nada. Pronto: o projeto é completamente offline.

**A volta da story:** Esta história foi **reprovada na primeira revisão** — quem revisou rodou na máquina dele, caiu em cima do problema do arquivo remoto, e rejeitou. Não foi erro de execução, foi exatamente o ponto: se passou dessa vez, falharia na apresentação. A correção entrou, foi refeita e passou na segunda.

**ONDE:** `README.md`, `requirements.txt`, `data/raw/base_territorial_out25.zip`, todos os `notebooks/01-*` reexecutados

### US-19: Documentação de atualização mensal + aba do painel

**O QUÊ — Parte 1:** Novo arquivo `docs/atualizacao-mensal.md` — como o projeto ganha dados de um mês novo sem quebrar. Traz:
- O comando exato para rodá-lo.
- A ordem em que os 9 notebooks precisam ser reexecutados (o `01-pa6-perfil-demanda` usa o resultado de `01-indice-dependencia`; rodar fora da ordem, o resultado sai silenciosamente errado — tipo de bug que ninguém vê).
- Uma nota sobre as retificações de dezembro: o DATASUS corrige dados de meses passados retroativamente, então números podem mudar um pouco.

**O QUÊ — Parte 2:** Quinta aba no painel, chamada **"Sobre os dados"** — de onde vêm os números, por que funcionam sem internet, a ressalva de dezembro, quanto tempo leva pra atualizar. Responde a pergunta que o professor vai fazer no dia 07/08 sem o Pedro precisar decorar nada — é só ler do painel.

**POR QUÊ:** Um projeto de dados que ninguém sabe manter é um projecto que morre após a apresentação. A documentação garante que a Secretaria de Saúde consegue rodar novamente com dados novos, sem chamar de volta o Pedro. E a aba "Sobre os dados" cuida da confiança — mostrar a proveniência do número no mesmo lugar onde ele aparece é simples, mas surpreendentemente raro.

**ONDE:** `docs/atualizacao-mensal.md`, `app.py` (aba Sobre os dados)

*(O detalhe das 19 etapas anteriores está resumido em "Onde estamos", acima, e contado por inteiro em `docs/diario-do-projeto.md`.)*

## Pra você, Pedro

### Novo: notebook de estudo feito sob medida pra você

**Está pronto:** `notebooks/90-eda-guiada.ipynb`

Este é o material de estudo antes de apresentar — começando do básico e chegando até as 16 regiões. Cada pedaço de código tem explicação em português antes. Tem 3 momentos onde você coloca informação sua (cidade, comparação, região) e roda — responde à pergunta "quanto de evasão tem AQUI?" de verdade, não genérica.

Se digitar um nome que não existe, não quebra com erro feio — aparece mensagem orientando. Todos os 34 números foram conferidos contra as tabelas prontas: bateram todos. Vale também pela descoberta registrada ali: das 223 cidades da PB, só 62 têm internação SUS no ano; as outras 161 aparecem com 100% de evasão não porque perdem pacientes, mas porque não têm hospital. Um "ranking de evasão" não diz acesso à saúde nesses casos.

### Pendências que ficam pra você e pra dupla

Faltam **dois testes de leitura** — são coisas que você (ou vocês juntos) precisam fazer antes de apresentar, e agora estão desobstruídas porque o código ficou pronto:

**1. Teste de leitura do mapa (1 minuto)** — combinado antigo que continua valendo.
1. Abrir terminal na pasta e rodar: `streamlit run app.py`
2. Vai abrir navegador. Clicar em **Mapa** no alto.
3. Olhar por 1 minuto, sem ajuda. Depois me dizer: **quais são as cidades que puxam pacientes de toda a Paraíba?**

Se as duas principais saltarem aos olhos, passou. Se precisar procurar, o mapa é que está errado — corrijo antes de 07/08. Me responde por WhatsApp.

**2. Ensaio da demo em dupla** — novo este combinado.
Vocês dois precisam sentar e rodar o painel do zero até o fim, como se fosse no dia 07/08. Simula a apresentação: quem apresenta (você) fala, quem assiste (Augusto) observa sem interromper. Depois a gente corrige o que tiver saído confuso. Isso leva ~30 min e combina com 2 dias antes de 07/08. Dica pra combinar com o Augusto agora.

### O painel tem uma aba nova que responde as perguntas sobre origem dos dados

Abra e explore. Na aba **Sobre os dados**, está escrito: de onde vêm os números, por que funcionam sem internet, como atualizar com dados novos. Responde a pergunta que o professor vai fazer ("de onde saiu esse dado?") sem você precisar decorar nada — é só ler do painel.

### Já enquanto estiver no painel: estude também as abas de Índice e Achados

Abra a aba **Índice de dependência** — ela mostra o número principal do projeto em ranking das 16 regiões. Se o professor perguntar "o que é esse índice?", clica em um bloco e lê pra ele.

E a aba **Achados & recomendações** é a que você vai usar pra apresentar — os 7 achados com números, as 5 recomendações. Toda a conclusão da pesquisa lá resumida.

### Leitura importante: narrativa do projeto

Quando tiver tempo — recomendo hoje ou amanhã — abra:
```
reports/narrativa-executiva.md
```

É o texto da apresentação completo: achado central, 7 achados, 5 recomendações, fecho, limitações. **É exatamente o que você vai contar no dia 07/08, com números ao lado.** São ~4–5 páginas.

Se algum parágrafo ficar confuso pra você, fala pro Augusto — se você lê confuso, quem assiste também fica. Com 11 dias ainda dá tempo de reescrever.

### Quando você tiver tempo: familiarize-se com os números

**Caminho mais curto, em ordem:**
1. **`docs/diario-do-projeto.md`** — história do projeto inteira, etapa por etapa, poucas páginas. Rende mais por minuto gasto.
2. **Tabelas em Excel:** `data/processed/indice_dependencia_regional.csv` (índice das 16 regiões) e `outputs/tables/pa3_saldo_municipios.csv` (saldo por cidade). Olhar os números com seus olhos gruda muito mais.
3. **Gráficos em `outputs/figures/`** — são as imagens que vão pro slide. Vale saber de cor o que cada um mostra.

Se pensar "não sei explicar esse número se perguntarem", fala pro Augusto — faltam 11 dias, dá tempo. Com 1 dia de apresentação não dá mais.

### Explorar a base de dados (opcional, mas valioso)

Se quiser entender de verdade os dados, existe um material pronto pra isso:

1. **Preparar o projeto (uma vez só):** terminal na pasta, rodar: `pip install -r requirements.txt`
2. **Rodar Jupyter:** `jupyter notebook`, e num notebook novo:
   ```python
   import pandas as pd
   df = pd.read_parquet("data/processed/sih_pb_2025_regioes.parquet")
   ```
   Cada linha é uma internação. Colunas úteis: `nome_mun_res` (onde mora), `nome_mun_mov` (onde internou), `regiao_res` (região onde mora), `regiao_int` (região do hospital). Quando são diferentes = viajou.

3. **Roteiros prontos pra ler:**
   - `notebooks/01-tratamento-base.ipynb` — como o arquivo foi feito, em português.
   - `notebooks/01-regiao-saude.ipynb` — como a região foi colocada.
   - `notebooks/01-matriz-od.ipynb` — como a matriz O-D foi montada.
   - `docs/dicionario-dados.md` — o que cada coluna significa.

4. **Salvar seu notebook na pasta `notebooks/`** com nome começando em `90-`, ex: `90-eda-pedro.ipynb`. Perguntas boas: quais cidades mais mandam pacientes pra fora? Pra onde? Quais regiões mais perdem?

5. **Quando terminar:** GitHub Desktop → Commit → Push.

### Mudança anterior (mantida pra referência): dispensa do teste de leitura do índice

Se leu este arquivo dias atrás, tinha aqui um teste do índice de dependência marcado como bloqueador. **Não trava mais nada.** O Augusto leu o texto, achou claro pra quem raciocina bem, e desbloqueou — não é pendência sua. (Essa dispensa vale **só** pro índice; os testes do mapa e texto continuam valendo.)

## Combinados pra trabalharmos sem conflito

- **Cada um no seu quadrado:** Augusto mexe na pasta `src/` e nos notebooks começando com `01-`; você mexe nos notebooks começando com `90-` e na pasta `reports/`. Ninguém edita arquivo do outro — assim o GitHub nunca reclama de conflito.
- **Ritual sempre:** Pull antes de começar, Commit + Push quando terminar.
- Dúvida rápida → WhatsApp. Decisão importante → fica registrada aqui.
